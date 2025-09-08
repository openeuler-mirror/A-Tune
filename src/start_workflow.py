import logging
from typing import Dict, Any

from fastapi import FastAPI, HTTPException

from src.config import config
from src.performance_analyzer.performance_analyzer import PerformanceAnalyzer
from src.performance_collector.metric_collector import MetricCollector
from src.performance_collector.micro_dep_collector import (
    MicroDepCollector,
    COLLECTMODE,
)
from src.performance_collector.static_metric_profile_collector import (
    StaticMetricProfileCollector,
)
from src.performance_optimizer.param_recommender import ParamRecommender
from src.performance_optimizer.strategy_optimizer import StrategyOptimizer
from src.utils.config.app_config import AppInterface
from src.utils.shell_execute import SshClient
from src.start_tune import run_param_optimization, run_strategy_optimization

# ================= FastAPI 初始化 ===================
app = FastAPI(
    title="性能分析与优化 API",
    description="统一接口：Collector / Analyzer / Optimizer",
    version="1.0.0",
)

# ================= 全局配置与缓存 ===================
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
cache: Dict[str, Dict[str, Any]] = {}

host_ip = config["servers"][0]["ip"]
host_port = config["servers"][0]["port"]
host_user = config["servers"][0]["host_user"]
host_password = config["servers"][0]["password"]
app_name = config["servers"][0]["app"]
max_retries = config["servers"][0]["max_retries"]
delay = config["servers"][0]["delay"]


# ================= Collector 接口 ===================
@app.get("/collector")
def run_collector():
    if not host_ip:
        raise HTTPException(
            status_code=400, detail=f"需要输入待调优机器IP，否则无法采集数据"
        )
    ssh_client = SshClient(
        host_ip=host_ip,
        host_port=host_port,
        host_user=host_user,
        host_password=host_password,
        max_retries=max_retries,
        delay=delay,
    )

    # 1. 静态指标
    static_collector = StaticMetricProfileCollector(
        ssh_client=ssh_client, max_workers=5
    )
    static_profile = static_collector.run()

    # 2. 动态指标
    metric_collector = MetricCollector(
        ssh_client=ssh_client,
        app=app_name,
        pressure_test_mode=False,
    )
    metrics = metric_collector.run()

    # 3. 微依赖分析（可选）
    if config["feature"][0]["microDep_collector"]:
        micro_collector = MicroDepCollector(
            ssh_client=ssh_client,
            iteration=10,
            target_process_name=config["servers"][0]["target_process_name"],
            benchmark_cmd=config["benchmark_cmd"],
            mode=COLLECTMODE.DIRECT_MODE,
        )
        micro_dep = micro_collector.run()
        metrics["micro_dep"] = micro_dep

    # 缓存
    cache[host_ip] = {"metrics": metrics, "static_profile": static_profile}

    return {
        "data": {
            "static_profile": static_profile,
            "metrics": metrics,
        }
    }


# ================= Analyzer 接口 ===================
@app.get("/analyzer")
def run_analyzer():
    if not host_ip or host_ip not in cache or "metrics" not in cache[host_ip]:
        raise HTTPException(
            status_code=400, detail=f"{host_ip} 缺少 metrics，请先采集数据，再进行分析"
        )

    analyzer = PerformanceAnalyzer(
        data=cache[host_ip]["metrics"], app=app_name
    )
    report, bottleneck = analyzer.run()
    cache[host_ip]["report"] = report
    cache[host_ip]["bottleneck"] = bottleneck

    return {"report": report, "bottleneck": bottleneck}


# ================= Optimizer（参数+策略）接口 ===================
@app.get("/optimizer")
def run_optimizer():
    if (
            not host_ip
            or host_ip not in cache
            or "report" not in cache[host_ip]
            or "static_profile" not in cache[host_ip]
    ):
        raise HTTPException(
            status_code=400,
            detail=f"{host_ip} 缺少 report 或 static_profile，请先执行 /collector 和 /analyzer",
        )

    # --- 参数优化 ---
    ssh_client = SshClient(
        host_ip=host_ip,
        host_port=host_port,
        host_user=host_user,
        host_password=host_password,
        max_retries=max_retries,
        delay=delay,
    )

    param_recommender = ParamRecommender(
        service_name=app_name,
        slo_goal=0.1,
        performance_metric=AppInterface(ssh_client)
        .get(app_name)
        .performance_metric,
        static_profile=cache[host_ip]["static_profile"],
        performance_analysis_report=cache[host_ip]["report"],
        ssh_client=ssh_client,
    )
    param_opt_result = param_recommender.run(history_result=None)

    # --- 策略优化 ---
    strategy_opt = StrategyOptimizer(
        application=app_name,
        bottle_neck=cache[host_ip]["bottleneck"],  # fallback
        host_ip=host_ip,
        host_port=host_port,
        host_user=host_user,
        host_password=host_password,
        system_report=cache[host_ip]["report"],
        target_config_path="",
    )
    recommendations = strategy_opt.get_recommendations_json(
        bottleneck=cache[host_ip]["bottleneck"],
        top_k=1,
        business_context="高并发Web服务，CPU负载主要集中在用户态处理",
    )

    return {
        "param_optimization": param_opt_result,
        "strategy_recommendation": recommendations,
    }


# ================= tune（开始调优）接口 ===================
@app.get("/start_tune")
def tune():
    feature_cfg = config["feature"][0]
    report = cache[host_ip]["report"]
    bottleneck = cache[host_ip]["bottleneck"]
    server_cfg = config["servers"][0]
    static_profile_info = cache[host_ip]["static_profile"]
    ssh_client = SshClient(
        host_ip=host_ip,
        host_port=host_port,
        host_user=host_user,
        host_password=host_password,
        max_retries=max_retries,
        delay=delay,
    )
    run_param_optimization(
        server_cfg["app"], report, static_profile_info, ssh_client,
        feature_cfg["need_restart_application"], feature_cfg["pressure_test_mode"],
        feature_cfg["tune_system_param"], feature_cfg["tune_app_param"], feature_cfg["need_recover_cluster"],
        feature_cfg["benchmark_timeout"]
    )
    if feature_cfg["strategy_optimization"]:
        run_strategy_optimization(ssh_client, server_cfg["app"], bottleneck, server_cfg, report)
    return "调优执行完成"


def main():
    import uvicorn

    uvicorn.run(app=app, host="0.0.0.0", port=8092)


if __name__ == "__main__":
    main()
