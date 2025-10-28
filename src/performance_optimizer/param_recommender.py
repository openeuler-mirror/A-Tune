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

from src.utils.prompt_instance import prompt_manager

class ParamRecommender:
    def __init__(
            self,
            service_name: str,
            slo_goal: float,
            performance_metric: PerformanceMetric,
            static_profile: str,
            performance_analysis_report: str,
            all_params,
            params_set,
            chunk_size=20,
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
        self.ssh_client = ssh_client
        self.all_params = all_params
        self.params_set = params_set
        self.chunk_size = chunk_size
        self.performance_analysis_report = performance_analysis_report

    def _get_histort(self, history_result, cur_params_set):
        target_keys = {s.split(':', 1)[0] for s in cur_params_set}

        history_entries = []

        # 1. 上一轮
        if "上一轮调优结果" in history_result:
            entry = history_result["上一轮调优结果"]
            if isinstance(entry, dict) and "参数推荐" in entry:
                history_entries.append((
                    f"上一轮性能: {entry.get('上一轮性能', 'N/A')}",
                    entry["参数推荐"]
                ))

        # 2. 历史最佳
        if "历史最佳结果" in history_result:
            entry = history_result["历史最佳结果"]
            if isinstance(entry, dict) and "参数推荐" in entry:
                history_entries.append((
                    f"历史最佳: {entry.get('最佳性能', 'N/A')}",
                    entry["参数推荐"]
                ))

        # 3. 历史最差
        if "历史最差结果" in history_result:
            entry = history_result["历史最差结果"]
            if isinstance(entry, dict) and "参数推荐" in entry:
                history_entries.append((
                    f"历史最差: {entry.get('最差性能', 'N/A')}",
                    entry["参数推荐"]
                ))

        # 过滤参数
        filtered_history = [
            (
                improve_text,
                {k: v for k, v in recommend_params.items() if k in target_keys}
            )
            for improve_text, recommend_params in history_entries
        ]
        return filtered_history

    def _process_chunk(self, history_result, cur_params_set, is_positive):
        history_result = self._get_histort(history_result, cur_params_set)

        params_set_str = ",".join(cur_params_set)
        allowed_set = set([
            "self.service_name",
            "self.performance_metric.name",
            "self.performance_metric.value",
            "self.slo_goal",
            "self.static_profile",
            "history_result",
            "self.performance_analysis_report",
            "params_set_str",
        ])
        prompt_mode = prompt_manager.get_mode(self.service_name)
        if prompt_mode == "fast":
            recommend_prompt_format = prompt_manager.get(self.service_name, prompt_mode, 'recommender')['value']
            recommend_prompt, extras = prompt_manager.render_by_parse(recommend_prompt_format, allowed_set)
            if len(extras) != 0:
                logging.warn(f"param not in custom offered param {extras}")
            recommended_params = get_llm_response(recommend_prompt)
        elif prompt_mode == "normal":
            idea_prompt_format = prompt_manager.get(self.service_name, prompt_mode, 'idea')['value']
            idea_prompt, extras = prompt_manager.render_by_parse(idea_prompt_format, allowed_set)
            optimization_idea = get_llm_response(idea_prompt)
            allowed_set.add("optimization_idea")
            recommend_prompt_format = prompt_manager.get(self.service_name, prompt_mode,
                'recommender_positive' if is_positive else 'recommender_negative')['value']
            recommend_prompt, extras = prompt_manager.render_by_parse(recommend_prompt_format, allowed_set)
            recommended_params = get_llm_response(recommend_prompt)
        else:
            # todo for slow prompt
            recommended_params = get_llm_response(recommend_prompt)

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
            [{self.service_name}类] 你是专业的系统运维专家。当前性能指标未达预期，但上一轮调优为正向结果（性能提升或无退化）。
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
            4) 必须满足依赖/互斥/上限下限/类型与单位要求。
            5) 每个参数的推荐值必须可被系统实际接受并确保应用可启动。
            6) 若无合适变更，输出空json对象。

            输出格式（必须严格遵守）：
            - 仅输出一个 JSON 对象，键为“可调参数名称”，值为“推荐取值”。
            - 不要输出任何多余文字、说明、示例、代码围栏或注释。
            """

        else:
            prompt = f"""
            [{self.service_name}类] 你是专业的系统运维专家。当前性能指标未达预期，且上一轮调优为负向结果（性能下降/不稳定/报错等）。
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
            4) 必须满足依赖/互斥/上限下限/类型与单位要求。
            5) 每个参数的推荐值必须可被系统实际接受并确保应用可启动。
            6) 若无合适变更，输出空json对象。

            输出格式（必须严格遵守）：
            - 仅输出一个 JSON 对象，键为“可调参数名称”，值为“推荐取值”。
            - 不要输出任何多余文字、说明、示例、代码围栏或注释。
            """

        response = get_llm_response(prompt, max_tokens=1024)
        return response

