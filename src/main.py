from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any
import logging

from src.performance_collector.metric_collector import MetricCollector
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
from src.performance_optimizer.param_optimizer import ParamOptimizer
from src.utils.shell_execute import SshClient
from src.utils.metrics import PerformanceMetric
from src.config import config

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


class SSHInput(BaseModel):
    ip: str
    port: int
    user: str
    password: str


# ================= Collector 接口 ===================
@app.post("/collector")
def run_collector(ssh: SSHInput):
    ssh_client = SshClient(
        host_ip=ssh.ip,
        host_port=ssh.port,
        host_user=ssh.user,
        host_password=ssh.password,
        max_retries=3,
        delay=1,
    )

    # 1. 静态指标
    static_collector = StaticMetricProfileCollector(
        ssh_client=ssh_client, max_workers=5
    )
    static_profile = static_collector.run()

    # 2. 动态指标
    metric_collector = MetricCollector(
        ssh_client=ssh_client,
        host_ip=ssh.ip,
        host_port=ssh.port,
        host_user=ssh.user,
        host_password=ssh.password,
        app=config["servers"][0]["app"],
        pressure_test_mode=config["feature"][0]["pressure_test_mode"],
    )
    metrics = metric_collector.run()

    # 3. 微依赖分析（可选）
    if config["feature"][0]["microDep_collector"]:
        host_info = HostInfo(
            host_ip=ssh.ip,
            host_port=ssh.port,
            host_password=ssh.password,
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
    cache[ssh.ip] = {
        "metrics": metrics,
    }

    return {
        "data": {
            "static_profile": static_profile,
            "metrics": metrics,
        }
    }


# ================= Analyzer 接口 ===================
@app.get("/analyzer")
def run_analyzer(ip: str = Query(..., description="目标服务器 IP")):
    if ip not in cache or "metrics" not in cache[ip]:
        raise HTTPException(
            status_code=400, detail=f"{ip} 缺少 metrics，请先执行 /collector"
        )

    analyzer = PerformanceAnalyzer(
        data=cache[ip]["metrics"], app=config["servers"][0]["app"]
    )
    report, _ = analyzer.run()
    cache[ip]["report"] = report

    return {"report": report}


# ================= Optimizer（参数+策略）接口 ===================
@app.get("/optimizer")
def run_optimizer(ip: str = Query(..., description="目标服务器 IP")):
    if (
        ip not in cache
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
        host_port=config["servers"][0]["port"],
        host_user=config["servers"][0]["host_user"],
        host_password=config["servers"][0]["password"],
        max_retries=3,
        delay=1,
    )

    def slo_calc_callback(baseline, benchmark_result):
        if baseline is None or abs(baseline) < 1e-9:
            return 0.0
        return (benchmark_result - baseline) / baseline

    param_opt = ParamOptimizer(
        service_name=config["servers"][0]["app"],
        performance_metric=PerformanceMetric.QPS,
        slo_goal=0.1,
        analysis_report=cache[ip]["report"],
        static_profile=cache[ip]["static_profile"],
        ssh_client=ssh_client,
        slo_calc_callback=slo_calc_callback,
        max_iterations=1,
        need_restart_application=config["feature"][0]["need_restart_application"],
        pressure_test_mode=config["feature"][0]["pressure_test_mode"],
    )
    param_opt_result = param_opt.run()

    # --- 策略优化 ---
    strategy_opt = StrategyOptimizer(
        application=config["servers"][0]["app"],
        bottle_neck=param_opt.analysis_report.get("瓶颈信息", {}),  # fallback
        host_ip=ip,
        host_port=config["servers"][0]["port"],
        host_user=config["servers"][0]["host_user"],
        host_password=config["servers"][0]["password"],
        system_report=cache[ip]["report"],
        target_config_path="",
    )
    recommendations = strategy_opt.get_recommendations_json(
        bottleneck=param_opt.analysis_report.get("瓶颈信息", {}),
        top_k=1,
        business_context="高并发Web服务，CPU负载主要集中在用户态处理",
    )

    return {
        "param_optimization": param_opt_result,
        "strategy_recommendation": recommendations,
    }
