import logging

from src.performance_collector.micro_dep_collector import MicroDepCollector, COLLECTMODE
from src.config import config
from src.performance_analyzer.performance_analyzer import PerformanceAnalyzer
from src.performance_collector.metric_collector import MetricCollector
from src.performance_collector.static_metric_profile_collector import StaticMetricProfileCollector
from src.performance_optimizer.param_optimizer import ParamOptimizer
from src.performance_optimizer.strategy_optimizer import StrategyOptimizer
from src.performance_test.pressure_test import PressureTest
from src.utils.collector.collector_trigger import TriggerEventListener
from src.utils.common import display_metrics
from src.utils.shell_execute import SshClient


def setup_logging():
    """配置日志格式与级别"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def create_ssh_client(server_cfg):
    """根据配置创建 SSH 客户端"""
    return SshClient(
        host_ip=server_cfg["ip"],
        host_port=server_cfg["port"],
        host_user=server_cfg["host_user"],
        host_password=server_cfg["password"],
        max_retries=server_cfg["max_retries"],
        delay=server_cfg["delay"],
    )


def collect_static_metrics(ssh_client):
    """采集静态指标"""
    static_collector = StaticMetricProfileCollector(ssh_client=ssh_client, max_workers=5)
    static_profile_info = static_collector.run()
    display_metrics(static_profile_info["static"], headers=["指标名称", "指标值"])
    return static_profile_info


def run_pressure_test_if_needed(server_cfg, ssh_client, enabled):
    """如果启用压测模式，则执行压测准备和触发器"""
    if not enabled:
        return
    logging.info("[Main] start pressure test ...")
    pressure_test = PressureTest(server_cfg["app"], ssh_client)
    listener = TriggerEventListener().configure(
        host=server_cfg["ip"],
        port=server_cfg["port"],
        user=server_cfg["host_user"],
        password=server_cfg["password"],
    )
    listener.run()
    pressure_test.start()


def collect_runtime_metrics(ssh_client, server_cfg, pressure_test_mode):
    """采集运行时性能指标"""
    metric_collector = MetricCollector(
        ssh_client=ssh_client,
        app=server_cfg["app"],
        pressure_test_mode=pressure_test_mode,
    )
    data = metric_collector.run()
    display_metrics(data, headers=["负载类型", "指标名", "指标值"])
    return data


def collect_micro_dependencies_if_needed(ssh_client, data, server_cfg, need_micro_dep):
    """如果需要，采集微依赖信息"""
    if not need_micro_dep:
        return data
    micro_dep_collector = MicroDepCollector(
        ssh_client=ssh_client,
        iteration=10,
        target_process_name=server_cfg["target_process_name"],
        benchmark_cmd=config["benchmark_cmd"],
        mode=COLLECTMODE.DIRECT_MODE,
    )
    micro_dep_data = micro_dep_collector.run()
    logging.info(f"MicroDepCollector data: {micro_dep_data}")
    data["micro_dep"] = micro_dep_data
    return data


def analyze_performance(data, app):
    """分析性能瓶颈"""
    logging.info("[Main] analyzing performance ...")
    analyzer = PerformanceAnalyzer(data=data, app=app)
    return analyzer.run()


def run_param_optimization(app, report, static_profile_info, ssh_client, need_restart, pressure_mode, tune_system_param,
                           tune_app_param, need_recover_cluster, benchmark_timeout):
    """执行参数优化"""

    def slo_calc_callback(baseline, benchmark_result, symbol):
        if baseline is None or abs(baseline) < 1e-9:
            return 0.0
        return symbol * (benchmark_result - baseline) / baseline

    optimizer = ParamOptimizer(
        service_name=app,
        slo_goal=0.1,
        analysis_report=report,
        static_profile=static_profile_info,
        ssh_client=ssh_client,
        slo_calc_callback=slo_calc_callback,
        max_iterations=20,
        need_restart_application=need_restart,
        pressure_test_mode=pressure_mode,
        tune_system_param=tune_system_param,
        tune_app_param=tune_app_param,
        need_recover_cluster=need_recover_cluster,
        benchmark_timeout=benchmark_timeout
    )
    optimizer.run()


def run_strategy_optimization(ssh_client, app, bottleneck, server_cfg, report):
    """执行策略优化并输出推荐"""
    strategy_optimizer = StrategyOptimizer(
        application=app,
        bottle_neck=bottleneck,
        ssh_client=ssh_client,
        system_report=report,
        target_config_path="",
    )
    recommendations = strategy_optimizer.get_recommendations_json(
        bottleneck, top_k=1, business_context=server_cfg["business_context"]
    )
    logging.info("推荐策略:", recommendations)


def main():
    setup_logging()
    server_cfg = config["servers"][0]
    feature_cfg = config["feature"][0]

    ssh_client = create_ssh_client(server_cfg)

    static_profile_info = collect_static_metrics(ssh_client)
    run_pressure_test_if_needed(server_cfg, ssh_client, feature_cfg["pressure_test_mode"])

    metrics_data = collect_runtime_metrics(ssh_client, server_cfg, feature_cfg["pressure_test_mode"])
    metrics_data = collect_micro_dependencies_if_needed(ssh_client, metrics_data, server_cfg,
                                                        feature_cfg["microDep_collector"])

    report, bottleneck = analyze_performance(metrics_data, server_cfg["app"])
    logging.info(f">>> PerformanceAnalyzer运行结果：{report} {bottleneck}")

    run_param_optimization(
        server_cfg["app"], report, static_profile_info, ssh_client,
        feature_cfg["need_restart_application"], feature_cfg["pressure_test_mode"],
        feature_cfg["tune_system_param"], feature_cfg["tune_app_param"], feature_cfg["need_recover_cluster"],
        feature_cfg["benchmark_timeout"]
    )
    if feature_cfg["strategy_optimization"]:
        run_strategy_optimization(ssh_client, server_cfg["app"], bottleneck, server_cfg, report)


if __name__ == "__main__":
    main()
