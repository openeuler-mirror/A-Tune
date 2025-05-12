from src.performance_collector.metric_collector import MetricCollector
from src.performance_analyzer.performance_analyzer import PerformanceAnalyzer
from src.performance_optimizer.knob_optimizer import KnobOptimizer
from src.performance_collector.metric_profile_collector import MetricProfileCollector

from src.utils.shell_execute import SshClient

ssh_client = SshClient(
    host_ip="YOUR_IP",
    host_port=22,
    host_user="root",
    host_password="YOUR_PWD",
    max_retries=3,
    delay=1.0    
)

metric_collector = MetricProfileCollector(
    ssh_client=ssh_client,
    max_workers=5 
)

static_profile_info = metric_collector.run()

print(static_profile_info)

app="mysql"
testCollector = MetricCollector(
    host_ip="YOUR_IP",
    host_port=22,
    host_user="root",
    host_password="YOUR_PWD",
    app=app
)
data = testCollector.run()

print(data)

testAnalyzer = PerformanceAnalyzer(
    data=data
)
report, bottleneck = testAnalyzer.run()
print(report, bottleneck)