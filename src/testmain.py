import logging

from src.performance_collector.metric_collector import MetricCollector
from src.performance_analyzer.performance_analyzer import PerformanceAnalyzer
from src.performance_optimizer.strategy_optimizer import StrategyOptimizer
from src.performance_collector.static_metric_profile_collector import (
    StaticMetricProfileCollector,
)

from src.utils.collector.collector_trigger import TriggerEventListener
from src.utils.shell_execute import SshClient
from src.config import config
from src.utils.common import display_metrics

from src.performance_test.pressure_test import PressureTest
from performance_collector.micro_dep_collector import (
    MicroDepCollector,
    HostInfo,
    COLLECTMODE,
)
from src.performance_optimizer.param_optimizer import ParamOptimizer
from src.utils.metrics import PerformanceMetric

logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format="%(asctime)s - %(levelname)s - %(message)s",  # 设置日志格式
    datefmt="%Y-%m-%d %H:%M:%S",  # 设置时间格式
)
# logging.disable(logging.CRITICAL)

host_ip = config["servers"][0]["ip"]
host_port = config["servers"][0]["port"]
host_user = config["servers"][0]["host_user"]
host_password = config["servers"][0]["password"]
app = config["servers"][0]["app"]
max_retries = config["servers"][0]["max_retries"]
delay = config["servers"][0]["delay"]
target_process_name = config["servers"][0]["target_process_name"]
benchmark_cmd = config["benchmark_cmd"]
need_restart_application = config["feature"][0]["need_restart_application"]
need_microDep_collector = config["feature"][0]["microDep_collector"]
pressure_test_mode = config["feature"][0]["pressure_test_mode"]
business_context = config["servers"][0]["business_context"]
enable_system_tuning = config["feature"][0]["enable_system_tuning"]


ssh_client = SshClient(
    host_ip=host_ip,
    host_port=host_port,
    host_user=host_user,
    host_password=host_password,
    max_retries=max_retries,
    delay=delay,
)

static_metric_collector = StaticMetricProfileCollector(
    ssh_client=ssh_client, max_workers=5
)
static_profile_info = static_metric_collector.run()
display_metrics(static_profile_info["static"], headers=["指标名称", "指标值"])

if pressure_test_mode:
    logging.info(f"[Main] start pressure test ...")
    # 压测模式若开启，则采集前通过压测模拟负载环境，压测期间采集负载数据
    # 压测模式若关闭，则按照流程执行benchmark作为基线
    pressure_test = PressureTest(app, ssh_client)
    trigger_event_listener = TriggerEventListener().configure(timeout=300)
    trigger_event_listener.run()
    pressure_test.start()

metric_collector = MetricCollector(
    ssh_client=ssh_client,
    host_ip=host_ip,
    host_port=host_port,
    host_user=host_user,
    host_password=host_password,
    app=app,
    pressure_test_mode=pressure_test_mode,
)
data = metric_collector.run()
display_metrics(data, headers=["负载类型", "指标名", "指标值"])

host_info = HostInfo(host_ip=host_ip, host_port=host_port, host_password=host_password)
collect_mode = COLLECTMODE.DIRECT_MODE
if need_microDep_collector:
    microDepCollector = MicroDepCollector(
        host_info=host_info,
        iteration=10,
        target_process_name=target_process_name,
        benchmark_cmd=benchmark_cmd,
        mode=collect_mode,
    )
    micro_dep_dollector_data = microDepCollector.run()
    print("microDepCollector data", micro_dep_dollector_data)
    data["micro_dep"] = micro_dep_dollector_data

logging.info("[Main] analyzing performance ...")
testAnalyzer = PerformanceAnalyzer(data=data, app=app)
report, bottleneck = testAnalyzer.run()
print(">>> PerformanceAnalyzer运行结果：", report, bottleneck)


def slo_calc_callback(baseline, benchmark_result, symbol):
    if baseline is None or abs(baseline) < 1e-9:
        return 0.0
    return symbol * (benchmark_result - baseline) / baseline


param_optimizer = ParamOptimizer(
    service_name=app,
    slo_goal=0.1,
    analysis_report=report,
    static_profile=static_profile_info,
    ssh_client=ssh_client,
    slo_calc_callback=slo_calc_callback,
    max_iterations=1,
    need_restart_application=need_restart_application,
    pressure_test_mode=pressure_test_mode,
    enable_system_tuning=enable_system_tuning
)
param_optimizer.run()

strategy_optimizer = StrategyOptimizer(
    application=app,
    bottle_neck=bottleneck,
    host_ip=host_ip,
    host_port=host_port,
    host_user=host_user,
    host_password=host_password,
    system_report=report,
    target_config_path="",
)
recommendations = strategy_optimizer.get_recommendations_json(
    bottleneck, top_k=1, business_context=business_context
)
print("推荐策略:", recommendations)
