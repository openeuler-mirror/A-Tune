import logging

from src.performance_collector.metric_collector import MetricCollector
from src.performance_analyzer.performance_analyzer import PerformanceAnalyzer
from src.performance_optimizer.knob_optimizer import KnobOptimizer
from src.performance_optimizer.strategy_optimizer import StrategyOptimizer
from src.performance_collector.static_metric_profile_collector import StaticMetricProfileCollector

from src.utils.shell_execute import SshClient
from src.config import config
from src.performance_benchmark.apply_mysql_params import apply_mysql_config


from performance_collector.micro_dep_collector import MicroDepCollector, HostInfo, COLLECTMODE
from src.performance_optimizer.param_optimizer import ParamOptimizer
from src.utils.metrics import PerformanceMetric
from src.performance_benchmark.mysql_benchmark import parse_mysql_sysbench


# logging.basicConfig(
#     level=logging.INFO,  # 设置日志级别
#     format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志格式
#     datefmt='%Y-%m-%d %H:%M:%S'  # 设置时间格式
# )
logging.disable(logging.CRITICAL)

host_ip = config["servers"][0]["ip"]
host_password = config["servers"][0]["password"]
app="mysql"

ssh_client = SshClient(
    host_ip=host_ip,
    host_port=22,
    host_user="root",
    host_password=host_password,
    max_retries=3,
    delay=1.0    
)

#logging.info(">>> 运行MetricProfileCollector：")
print(">>> 运行MetricProfileCollector：")
static_metric_collector = StaticMetricProfileCollector(
    ssh_client=ssh_client,
    max_workers=5 
)
static_profile_info = static_metric_collector.run()
print("static_profile:", static_profile_info)


host_info = HostInfo(host_ip="9.82.230.156",host_port=22, host_password="Huawei12#$")
target_pid = 2144391
benchmark_cmd = "tail -f /dev/null"
collect_mode = COLLECTMODE.ATTACH_MODE
microDepCollector = MicroDepCollector(
    host_info=host_info,
    iteration=10,
    target_pid=target_pid,
    benchmark_cmd=benchmark_cmd,
    mode=collect_mode,
)
micro_dep_dollector_data = microDepCollector.run()
print("microDepCollector data", micro_dep_dollector_data)

print(">>> 运行MetricCollector：")
metric_collector = MetricCollector(
    host_ip=host_ip,
    host_port=22,
    host_user="root",
    host_password=host_password,
    app=app
)
data = metric_collector.run()
data["micro_dep"] = micro_dep_dollector_data
print("metric_collector data:", data)

print(">>> 运行PerformanceAnalyzer：")
testAnalyzer = PerformanceAnalyzer(
    data=data
)
report, bottleneck = testAnalyzer.run()
print(">>> PerformanceAnalyzer运行结果：",report, bottleneck)


def slo_calc_callback(baseline, benchmark_result):
    if baseline is None or abs(baseline) < 1e-9:
        return 0.0
    return (benchmark_result - baseline) / baseline

def benchmark_callback(ssh_client):
    print("🔄 正在验证mysql benchmark性能...")
    result = parse_mysql_sysbench(ssh_client)
    try:
        return float(result.output["qps"])
    except ValueError:
        return 0.0

param_optimizer = ParamOptimizer(
    service_name="mysql",
    performance_metric=PerformanceMetric.QPS,
    slo_goal=0.1,
    analysis_report=report,
    static_profile=static_profile_info,
    ssh_client=ssh_client,
    slo_calc_callback=slo_calc_callback,
    benchmark_callback=benchmark_callback,
    apply_params_callback=apply_mysql_config,
    max_iterations = 1,
)
param_optimizer.run()

strategy_optimizer = StrategyOptimizer(
    application="mysql",
    bottle_neck=bottleneck,
    host_ip=host_ip,
    host_port=22,
    host_user="root",
    host_password=host_password,
    system_report=report,
    target_config_path=""
)
plan, isfinish, feedback = strategy_optimizer.run()
print("plan:", plan)
print("isfinish", isfinish)
print("feedback", feedback)