from performance_collector.metric_collector import MetricCollector
from performance_analyzer.performance_analyzer import PerformanceAnalyzer
from performance_optimizer.knob_optimizer import KnobOptimizer

testCollector = MetricCollector(
    host_ip="192.168.1.1",
    host_port=22,
    host_user="root",
    host_password="123456",
    app="mysql"
)
data = testCollector.run()
print(data)

testAnalyzer = PerformanceAnalyzer(
    data=data
)
report, bottleneck = testAnalyzer.run()
print(report, bottleneck)

testKnob = KnobOptimizer(
    application="mysql",
    bottle_neck="cpu",
    host_ip="192.168.1.1",
    host_port=22,
    host_user="root",
    host_password="123456",
    system_report=report,
    target_config_path=""
)
plan, isfinish, feedback = testKnob.run()
print(plan, isfinish, feedback)