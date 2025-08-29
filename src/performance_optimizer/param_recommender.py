import logging

from src.performance_analyzer.performance_analyzer import PerformanceAnalyzer
from src.performance_collector.metric_collector import MetricCollector
from src.performance_collector.static_metric_profile_collector import (
    StaticMetricProfileCollector,
)
from src.performance_optimizer.param_knowledge import ParamKnowledge
from src.utils.json_repair import json_repair
from src.utils.llm import get_llm_response
from src.utils.metrics import PerformanceMetric
from src.utils.shell_execute import SshClient
from src.utils.thread_pool import thread_pool_manager

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
            ssh_client=None,
            tune_system_param: bool = False,
            tune_app_param: bool = True
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
        self.param_knowledge = ParamKnowledge(
            ssh_client=ssh_client,
            tune_system_param=tune_system_param,
            tune_app_param=tune_app_param
        )
        self.all_params = self.param_knowledge.get_params(service_name)
        self.ssh_client = ssh_client
        self.params_set = self.param_knowledge.describe_param_background_knob(
            service_name, self.all_params
        )
        self.chunk_size = chunk_size
        self.performance_analysis_report = performance_analysis_report

    def _process_chunk(self, history_result, cur_params_set, is_positive):
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
            history_result, optimized_idea, cur_params_set, is_positive
        )

        recommended_params_set = json_repair(recommended_params)

        result = {}
        for param_name, param_value in recommended_params_set.items():
            if param_name in self.all_params:
                result[param_name] = param_value
        return result

    def run(self, history_result, is_positive=True):
        resultset = {}

        for i in range(0, len(self.params_set), self.chunk_size):
            cur_params_set = self.params_set[i: i + self.chunk_size]
            # 提交任务给线程池，返回 future-like 对象（你线程池需要支持这个）
            thread_pool_manager.add_task(
                self._process_chunk, history_result, cur_params_set, is_positive
            )

        thread_pool_manager.run_all_tasks()
        task_results = thread_pool_manager.get_all_results()

        for task_result in task_results:
            if task_result.status_code != 0:
                raise RuntimeError(
                    f"failed to execute task {task_result.func_name}, exception is {task_result.result}"
                )
            resultset.update(task_result.result)

        return resultset

    def recommend(self, history_result, optimization_idea, cur_params_set, is_positive):
        history_result = str(history_result) if history_result else "无"
        params_set_str = "\n".join(cur_params_set)
        if is_positive:
            prompt = f"""
            你是专业的系统运维专家。当前性能指标未达预期，但上一轮调优为正向结果（性能提升或无退化）。
            请在“心中完成推理”，只输出最终 JSON；除 JSON 以外不要输出任何文字、代码块或注释。

            目标：基于以下信息，在保持上轮有效方向的前提下，总结参数调整经验，进一步微调参数（在安全边界内适度加大力度），仅给出需要变更的参数与推荐新值。

            当前环境配置信息：
            {self.static_profile}

            历史调优信息（包含已修改参数与结果）：
            {history_result}

            调优思路：
            {optimization_idea}

            可调整参数全集（含类型/范围/枚举/默认值等）以及baseline对应的的取值为：
            {params_set_str}

            严格规则（务必遵守）：
            1) 仅输出与当前配置相比“需要变化”的参数；不相关或无收益的参数不要输出。
            2) 优先沿“上轮有效”的方向小步前进：连续型参数按原步长的 100%~150% 微增（通常为 +10%~+30%），离散/枚举取更激进且仍在安全范围的相邻档位；避免一次性过大变更（单参数变更幅度不超过 2 倍或 ±30%，取更严格者）。
            3) 不要动已证明对性能“无影响”的参数；避免同时调整明显互斥的参数。
            4) 必须满足依赖/互斥/上限下限/类型与单位要求；数值默认单位为“字节”。若数值后带单位，请以字符串表示（如 "512MB"）。
            5) 每个参数的推荐值必须可被系统实际接受并确保应用可启动。
            6) 若无合适变更，输出空json对象。

            输出格式（必须严格遵守）：
            - 仅输出一个 JSON 对象，键为“可调参数名称”，值为“推荐取值”。
            - 不要输出任何多余文字、说明、示例、代码围栏或注释。
            """

        else:
            prompt = f"""
            你是专业的系统运维专家。当前性能指标未达预期，且上一轮调优为负向结果（性能下降/不稳定/报错等）。
            请在“心中完成推理”，只输出最终 JSON；除 JSON 以外不要输出任何文字、代码块或注释。

            目标：基于以下信息，总结历史调优经验中的baseline、最佳调优结果、最差调优结果以及上一轮调优结果以及参数取值，反向微调上轮可能导致退化的参数，并选择更保守且安全的值；仅给出需要变更的参数与推荐新值。

            当前环境配置信息：
            {self.static_profile}

            历史调优信息（包含已修改参数与结果）：
            {history_result}

            调优思路：
            {optimization_idea}

            可调整参数全集（含类型/范围/枚举/默认值等）以及baseline对应的的取值为：
            {params_set_str}

            严格规则（务必遵守）：
            1) 仅输出与当前配置相比“需要变化”的参数；不相关或无收益的参数不要输出。
            2) 对上轮参与变更且疑似致退化的参数：沿“相反方向”小步调整（幅度为上轮步长的 30%~50%，通常为 -10%~-20%）；必要时关闭可选的高开销特性。
            3) 避免一次调整过多参数；不要同时调整互斥参数；优先选择风险更低的修正方案。
            4) 必须满足依赖/互斥/上限下限/类型与单位要求；数值默认单位为“字节”。若数值后带单位，请以字符串表示（如 "1GB"）。
            5) 每个参数的推荐值必须可被系统实际接受并确保应用可启动。
            6) 若无合适变更，输出空json对象。

            输出格式（必须严格遵守）：
            - 仅输出一个 JSON 对象，键为“可调参数名称”，值为“推荐取值”。
            - 不要输出任何多余文字、说明、示例、代码围栏或注释。
            """

        response = get_llm_response(prompt)
        return response

