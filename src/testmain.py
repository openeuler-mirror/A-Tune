import logging

from src.performance_collector.metric_collector import MetricCollector
from src.performance_analyzer.performance_analyzer import PerformanceAnalyzer
from src.performance_optimizer.knob_optimizer import KnobOptimizer
from src.performance_optimizer.strategy_optimizer import StrategyOptimizer
from src.performance_collector.metric_profile_collector import MetricProfileCollector

from src.utils.shell_execute import SshClient
from src.config import config

logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志格式
    datefmt='%Y-%m-%d %H:%M:%S'  # 设置时间格式
)

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

logging.info(">>> 运行MetricProfileCollector：")
metric_collector = MetricProfileCollector(
    ssh_client=ssh_client,
    max_workers=5 
)
static_profile_info = metric_collector.run()
logging.info(">>> MetricProfileCollector运行结果：")
logging.info(static_profile_info)

logging.info(">>> 运行MetricCollector：")
testCollector = MetricCollector(
    host_ip=host_ip,
    host_port=22,
    host_user="root",
    host_password=host_password,
    app=app
)
data = testCollector.run()
logging.info(">>> MetricCollector运行结果：")
logging.info(data)

logging.info(">>> 运行PerformanceAnalyzer：")
testAnalyzer = PerformanceAnalyzer(
    data=data
)
report, bottleneck = testAnalyzer.run()
logging.info(">>> PerformanceAnalyzer运行结果：")
logging.info(report)
logging.info(bottleneck)

logging.info(">>> 运行StrategyOptimizer：")
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
logging.info(">>> StrategyOptimizer运行结果：")
logging.info(plan)
logging.info(isfinish)
logging.info(feedback)