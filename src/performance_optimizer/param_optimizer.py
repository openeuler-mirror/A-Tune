from pydantic import BaseModel
from abc import abstractmethod
from typing import Dict, List, Any, Tuple
from src.utils.shell_execute import remote_execute
from src.utils.llm import get_llm_response
from src.utils.json_repair import json_repair
from src.performance_benchmark.mysql_benchmark import parse_mysql_sysbench
from src.performance_benchmark.apply_mysql_params import apply_mysql_config
import logging
from src.utils.shell_execute import SshClient
from src.performance_analyzer.performance_analyzer import PerformanceAnalyzer
from src.performance_optimizer.param_recommender import ParamRecommender
from src.performance_collector.metric_collector import MetricCollector
from src.performance_collector.static_metric_profile_collector import StaticMetricProfileCollector
from src.utils.metrics import PerformanceMetric

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ParamOptimizer:

    def __init__(
        self,
        service_name: str,
        performance_metric: PerformanceMetric,
        slo_goal: str,
        analysis_report: str,
        static_profile: str,
        ssh_client: SshClient,
        slo_calc_callback: callable,
        benchmark_callback: callable,
        apply_params_callback: callable,
        max_iterations: int = 10,
    ):
        self.analysis_report = analysis_report
        self.static_profile = static_profile
        self.ssh_client = ssh_client
        self.param_recommender = ParamRecommender(
            service_name=service_name,
            slo_goal=slo_goal,
            performance_metric=performance_metric,
            static_profile=static_profile,
            performance_analysis_report=analysis_report,
        )
        self.max_iterations = max_iterations
        # 计算slo指标提升方式的回调函数，输入是benchmark返回的性能指标，输出是业务性能提升比例
        self.slo_calc_callback = slo_calc_callback
        # 业务预期指标提升的目标
        self.slo_goal = slo_goal
        # 执行benchmark的回调函数
        self.benchmark_callback = benchmark_callback
        # 应用参数自动生效的回调函数
        self.apply_params_callback = apply_params_callback

    def calc_improve_rate(self, baseline, benchmark_result):
        return self.slo_calc_callback(baseline, benchmark_result)

    def reached_goal(self, baseline, benchmark_result):
        if self.calc_improve_rate(baseline, benchmark_result) >= self.slo_goal:
            return True
        return False

    def benchmark(self):
        return self.benchmark_callback(self.ssh_client)

    def apply_params(self, recommend_params):
        self.apply_params_callback(self.ssh_client, recommend_params)

    def run(self):
        # 运行benchmark，摸底参数性能指标
        baseline = self.benchmark()
        # 保存每轮调优的结果，反思调优目标是否达到
        history = []
        last_result = baseline
        best_result = baseline
        ratio = self.calc_improve_rate(baseline, last_result)
        print(
            f"[{1}/{self.max_iterations}] 性能基线是：{baseline}, 最佳结果：{best_result}, 上一轮结果:{last_result if last_result else baseline}, 性能提升：{ratio:.2%}"
        )

        for i in range(self.max_iterations):
            # 未达成目标的情况下，根据调优结果与历史最优的参数，执行参数调优推荐，给出参数名和参数值
            recommend_params = self.param_recommender.run(history_result=history)

            # 设置参数生效
            self.apply_params(recommend_params)

            # 执行benchmark，反馈调优结果
            performance_result = self.benchmark()

            # 达到预期效果，则退出循环
            if self.reached_goal(baseline, performance_result):
                break
            
            last_result = performance_result

            history.append(
                (
                    "提升{:.2%}".format(
                        self.calc_improve_rate(baseline, performance_result)
                    ),
                    recommend_params,
                )
            )
            if best_result is None:
                best_result = max(baseline, performance_result)
            else:
                best_result = max(best_result, performance_result)
            
            ratio = self.calc_improve_rate(baseline, last_result)

            print(
                f"[{i+1}/{self.max_iterations}] 性能基线是：{baseline}, 最佳结果：{best_result}, 上一轮结果:{last_result if last_result else baseline}, 性能提升：{ratio:.2%}"
            )

        print(
            f"调优完毕，{'达到' if self.reached_goal(baseline, best_result) else '未达到'} 预期目标"
        )


if __name__ == "__main__":
    from src.config import config
    ssh_client = SshClient(
        host_ip=config["servers"][0]["ip"],
        host_port=22,
        host_user="root",
        host_password=config["servers"][0]["password"],
        max_retries=3,
        delay=1.0,
    )

    metric_collector = StaticMetricProfileCollector(ssh_client=ssh_client, max_workers=5)

    static_profile = metric_collector.run()
    print("static_profile:", static_profile)

    print("正在采集负载信息...")
    app = "mysql"
    testCollector = MetricCollector(
        host_ip=config["servers"][0]["ip"],
        host_port=22,
        host_user="root",
        host_password=config["servers"][0]["password"],
        app=app,
    )
    data = testCollector.run()
    print("data:", data)
    print("正在分析负载信息...")
    testAnalyzer = PerformanceAnalyzer(data=data)
    performance_analysis_report, bottleneck = testAnalyzer.run()
    print("performance_analysis_report:", performance_analysis_report)
    print("bottleneck:", bottleneck)

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
        analysis_report=performance_analysis_report,
        static_profile=static_profile,
        ssh_client=ssh_client,
        slo_calc_callback=slo_calc_callback,
        benchmark_callback=benchmark_callback,
        apply_params_callback=apply_mysql_config,
    )

    param_optimizer.run()
