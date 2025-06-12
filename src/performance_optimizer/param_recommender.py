import logging
import json

from src.utils.llm import get_llm_response
from src.utils.json_repair import json_repair
from src.utils.config.global_config import param_config
from src.utils.config.app_config import AppInterface

from src.utils.metrics import PerformanceMetric
from src.utils.shell_execute import SshClient
from src.performance_analyzer.performance_analyzer import PerformanceAnalyzer

from src.performance_collector.metric_collector import MetricCollector
from src.performance_collector.static_metric_profile_collector import (
    StaticMetricProfileCollector,
)
from src.performance_optimizer.param_knowledge import ParamKnowledge

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
        enable_system_params=True,
        ssh_client=None,
    ):
        # 待调优app名称
        self.service_name = service_name
        # 业务性能调优目标，指标提升百分比
        self.slo_goal = slo_goal
        # 性能指标介绍
        self.performance_metric = performance_metric
        # 静态指标
        self.static_profile = "\n".join(f"{k}: {v}" for k, v in static_profile.items())
        # 可调参数知识库，用于给大模型描述应用参数背景知识
        self.param_knowledge = ParamKnowledge(ssh_client)
        self.all_params = self.param_knowledge.get_params(service_name)
        self.ssh_client = ssh_client
        self.params_set = self.param_knowledge.describe_param_background_knob(
            service_name, self.all_params
        )
        self.chunk_size = chunk_size
        self.performance_analysis_report = performance_analysis_report

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
            recommended_params_set = json_repair(recommended_params)
            for param_name, param_value in recommended_params_set.items():
                if param_name in self.all_params:
                    resultset[param_name] = param_value

        return resultset

    def recommend(self, history_result, optimization_idea, cur_params_set):
        history_result = str(history_result[-1]) if history_result else "无"
        params_set_str = "\n".join(cur_params_set)
        prompt = f"""
你是一个专业的系统运维专家,当前性能指标未达到预期，请你基于以下调优思路、当前环境的配置信息、可调整参数，选出可调整参数值。
请尽量精简描述，将终点需要调整的方向输出出来，不需要总结观点，对性能无影响的也不要输出。
当前环境的配置信息有：
{self.static_profile}
以下是历史调优的信息，历史调优修改了如下参数，你可以参考如下历史调优信息来反思可以可以改进的点: 
{history_result}
调优思路是：
{optimization_idea}
你可以调整的参数是：
{params_set_str}
请以json格式回答问题，key为可调参数名称，请根据上述的环境配置信息给出可调整的参数，若参数不相关则不要给出
value是可调参数的推荐取值，请根据上面的环境配置信息给出合理的具体取值，请仔细确认各个值是否可以被使用，避免设置后应用无法启动。
请注意若参数取值为数字类型，默认的单位为字节，请注意单位换算；若数字后面跟了单位，请使用字符串表示。
请勿给出除了json以外其他的回复,切勿增加注释。
"""
        response = get_llm_response(prompt)
        return response


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

    metric_collector = StaticMetricProfileCollector(
        ssh_client=ssh_client, max_workers=5
    )

    static_profile = metric_collector.run()

    app = "mysql"
    testCollector = MetricCollector(
        host_ip=config["servers"][0]["ip"],
        host_port=22,
        host_user="root",
        host_password=config["servers"][0]["password"],
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
