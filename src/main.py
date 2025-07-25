import logging
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Query

from src.config import config
from src.utils.shell_execute import SshClient
from src.utils.config.app_config import AppInterface
from src.performance_collector.metric_collector import MetricCollector
from src.performance_optimizer.param_recommender import ParamRecommender
from src.performance_analyzer.performance_analyzer import PerformanceAnalyzer
from src.performance_optimizer.strategy_optimizer import StrategyOptimizer
from src.performance_collector.static_metric_profile_collector import (
    StaticMetricProfileCollector,
)
from src.performance_collector.micro_dep_collector import (
    MicroDepCollector,
    HostInfo,
    COLLECTMODE,
)


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


host_port = config["servers"][0]["port"]
host_user = config["servers"][0]["host_user"]
host_password = config["servers"][0]["password"]
app = config["servers"][0]["app"]
max_retries = config["servers"][0]["max_retries"]
delay = config["servers"][0]["delay"]


# ================= Collector 接口 ===================
@app.get("/collector")
def run_collector(ip: str = Query(..., description="目标服务器 IP")):
    if not ip:
        raise HTTPException(
            status_code=400, detail=f"需要输入待调优机器IP，否则无法采集数据"
        )
    ssh_client = SshClient(
        host_ip=ip,
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
        host_ip=ip,
        host_port=host_port,
        host_user=host_user,
        host_password=host_password,
        app=app,
        pressure_test_mode=False,
    )
    metrics = metric_collector.run()

    # 3. 微依赖分析（可选）
    if config["feature"][0]["microDep_collector"]:
        host_info = HostInfo(
            host_ip=ip,
            host_port=host_port,
            host_password=host_password,
        )
        micro_collector = MicroDepCollector(
            host_info=host_info,
            iteration=10,
            target_process_name=config["servers"][0]["target_process_name"],
            benchmark_cmd=config["benchmark_cmd"],
            mode=COLLECTMODE.DIRECT_MODE,
        )
        micro_dep = micro_collector.run()
        metrics["micro_dep"] = micro_dep

    # 缓存
    cache[ip] = {"metrics": metrics, "static_profile": static_profile}

    return {
        "data": {
            "static_profile": static_profile,
            "metrics": metrics,
        }
    }


# ================= Analyzer 接口 ===================
@app.get("/analyzer")
def run_analyzer(ip: str = Query(..., description="目标服务器 IP")):
    if not ip or ip not in cache or "metrics" not in cache[ip]:
        raise HTTPException(
            status_code=400, detail=f"{ip} 缺少 metrics，请先执行 /collector"
        )

    analyzer = PerformanceAnalyzer(
        data=cache[ip]["metrics"], app=config["servers"][0]["app"]
    )
    report, bottleneck = analyzer.run()
    cache[ip]["report"] = report
    cache[ip]["bottleneck"] = bottleneck

    return {"report": report, "bottleneck": bottleneck}


# ================= Optimizer（参数+策略）接口 ===================
@app.get("/optimizer")
def run_optimizer(ip: str = Query(..., description="目标服务器 IP")):
    if (
        not ip
        or ip not in cache
        or "report" not in cache[ip]
        or "static_profile" not in cache[ip]
    ):
        raise HTTPException(
            status_code=400,
            detail=f"{ip} 缺少 report 或 static_profile，请先执行 /collector 和 /analyzer",
        )

    # --- 参数优化 ---
    ssh_client = SshClient(
        host_ip=ip,
        host_port=host_port,
        host_user=host_user,
        host_password=host_password,
        max_retries=max_retries,
        delay=delay,
    )

    param_recommender = ParamRecommender(
        service_name=config["servers"][0]["app"],
        slo_goal=0.1,
        performance_metric=AppInterface(ssh_client)
        .get(config["servers"][0]["app"])
        .performance_metric,
        static_profile=cache[ip]["static_profile"],
        performance_analysis_report=cache[ip]["report"],
        ssh_client=ssh_client,
    )
    param_opt_result = param_recommender.run(history_result=None)

    # --- 策略优化 ---
    strategy_opt = StrategyOptimizer(
        application=config["servers"][0]["app"],
        bottle_neck=cache[ip]["bottleneck"],  # fallback
        host_ip=ip,
        host_port=config["servers"][0]["port"],
        host_user=config["servers"][0]["host_user"],
        host_password=config["servers"][0]["password"],
        system_report=cache[ip]["report"],
        target_config_path="",
    )
    recommendations = strategy_opt.get_recommendations_json(
        bottleneck=cache[ip]["bottleneck"],
        top_k=1,
        business_context="高并发Web服务，CPU负载主要集中在用户态处理",
    )

    return {
        "param_optimization": param_opt_result,
        "strategy_recommendation": recommendations,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, host="0.0.0.0", port=8092)
