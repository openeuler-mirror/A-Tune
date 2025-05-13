import logging
import json

from src.utils.llm import get_llm_response
from src.utils.json_repair import json_repair


from src.utils.metrics import PerformanceMetric
from src.utils.shell_execute import SshClient
from src.performance_analyzer.performance_analyzer import PerformanceAnalyzer

from src.performance_collector.metric_collector import MetricCollector
from src.performance_collector.static_metric_profile_collector import StaticMetricProfileCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ParamRecommender:

    def __init__(
        self,
        service_name: str,
        slo_goal: float,
        performance_metric: PerformanceMetric,
        static_profile: str,
        performance_analysis_report: str,
        chunk_size=20,
    ):
        # 待调优app名称
        self.service_name = service_name
        # 业务性能调优目标，指标提升百分比
        self.slo_goal = slo_goal
        # 性能指标介绍
        self.performance_metric = performance_metric
        # 静态指标
        self.static_profile = "\n".join(f"{k}: {v}" for k, v in static_profile.items())
        # 可调参数知识库
        self.params_set = self.load_params_set()
        self.chunk_size = chunk_size
        self.performance_analysis_report = performance_analysis_report

    def load_params_set(self):
        params = []
        with open("./src/knowledge_base/params/mysql.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            params.append(f"{item['name']}:{item['info']['desc']}")
        return params

    def run(self, history_result):
        resultset = {}

        for i in range(0, len(self.params_set), self.chunk_size):
            cur_params_set = self.params_set[i : i + self.chunk_size]
            recommend_prompt = f"""
# CONTEXT # 
本次性能优化的目标为：
性能指标为{self.performance_metric.name}, 该指标的含义为：{self.performance_metric.value}，目标是提升{self.slo_goal:.2%}
性能分析报告：
{self.performance_analysis_report}
你可以分析的参数有：
{",".join(cur_params_set)}
# OBJECTIVE #
你是一个专业的系统运维专家,当前性能指标未达到预期，请你基于以上性能分析报告分析有哪些调优思路。
# Tone #
你应该尽可能秉承严肃、认真、严谨的态度
# AUDIENCE #
你的答案将会是其他系统运维专家的重要参考意见，请认真思考后给出你的答案。
"""
            optimized_idea = get_llm_response(recommend_prompt)
            recommended_params = self.recommend(
                history_result, optimized_idea, cur_params_set
            )
            resultset.update(json_repair(recommended_params))
        return resultset

    def recommend(self, history_result, optimization_idea, cur_params_set):
        history_result = str(history_result[-1]) if history_result else "无"
        params_set_str = "\n".join(cur_params_set)
        prompt = f"""
你是一个专业的系统运维专家,当前性能指标未达到预期，请你基于以下调优思路、当前环境的配置信息、可调整参数，选出可调整参数值。
当前环境的配置信息有：
{self.static_profile}
以下是历史调优的信息，历史调优修改了如下参数，你可以参考如下历史调优信息来反思可以可以改进的点: 
{history_result}
调优思路是：
{optimization_idea}
你可以调整的参数是：
{params_set_str}
请以json格式回答问题，key为可调参数名称，请根据上述的环境配置信息给出可调整的参数，若参数不相关则不要给出
value是可调参数的推荐取值，请根据上面的环境配置信息给出可用的具体取值，不要给无法使用的参数取值。
请勿给出除了json以外其他的回复。
"""
        response = get_llm_response(prompt)
        return response


if __name__ == "__main__":

    ssh_client = SshClient(
        host_ip="9.82.213.107",
        host_port=22,
        host_user="root",
        host_password="Huawei12#$",
        max_retries=3,
        delay=1.0,
    )

    metric_collector = StaticMetricProfileCollector(ssh_client=ssh_client, max_workers=5)

    static_profile = metric_collector.run()

    app = "mysql"
    testCollector = MetricCollector(
        host_ip="YOUR IP",
        host_port=22,
        host_user="root",
        host_password="YOUR PWD",
        app=app,
    )
    data = testCollector.run()

    testAnalyzer = PerformanceAnalyzer(data=data)
    performance_analysis_report, bottleneck = testAnalyzer.run()
    param_recommender = ParamRecommender(
        service_name="mysql",
        metric_objective="QPS",
        service_objective="10%",
        static_profile=static_profile,
        performance_analysis_report=performance_analysis_report,
    )

    response = param_recommender.run(history_result=None, baseline_result=43219.43)
    print(">>>>>>>>>>>>>>>>>>>>>>性能调优思路如下：")
    print(response)

    response = param_recommender.recommend(response)
    print(">>>>>>>>>>>>>>>>>>>>>>推荐参数如下：")
    print(response)
