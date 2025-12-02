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
from src.utils.common import translate

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
        if "previous_result" in history_result:
            entry = history_result["previous_result"]
            if isinstance(entry, dict) and "recommend_param" in entry:
                history_entries.append((
                    f"previous_performance: {entry.get('previous_performance', 'N/A')}",
                    entry["recommend_param"]
                ))

        # 2. 历史最佳
        if "best_result" in history_result:
            entry = history_result["best_result"]
            if isinstance(entry, dict) and "recommend_param" in entry:
                history_entries.append((
                    f"best_history: {entry.get('best_performance', 'N/A')}",
                    entry["recommend_param"]
                ))

        # 3. 历史最差
        if "worst_result" in history_result:
            entry = history_result["worst_result"]
            if isinstance(entry, dict) and "recommend_param" in entry:
                history_entries.append((
                    f"worst_history: {entry.get('worst_performance', 'N/A')}",
                    entry["recommend_param"]
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
            prompt = translate(
                f"""
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
            """,
                f"""
            [{self.service_name}] You are a professional system operations expert. The current performance metrics have not met expectations, but the previous round of optimization yielded positive results (performance improvement or no degradation).
            Please perform reasoning internally and output only the final JSON; do not output any text, code blocks, or comments other than the JSON.
            
            Objective: Based on the following information, summarize parameter adjustment experiences while maintaining the effective direction from the previous round, and further fine-tune the parameters (with a moderate increase in intensity within the safe boundaries). Only provide the parameters that need to be changed and their recommended new values.
            
            Current environment configuration information:
            {self.static_profile}
            
            Historical optimization information (including modified parameters and results):
            {history_result}
            
            Optimization approach:
            {optimization_idea}
           
            The full set of adjustable parameters (including type, range, enumeration, default value, etc.) and the baseline values corresponding to these parameters are:
            {params_set_str}
            
            Strict rules (must be followed):
            1) Output only the parameters that need to be changed compared to the current configuration; do not output any irrelevant or non-beneficial parameters.
            2) Prioritize making small steps in the direction that was effective in the previous round: for continuous parameters, increase them by 100% to 150% of the original step size (usually +10% to +30%); for discrete or enumerated parameters, choose a more aggressive but still safe adjacent value. Avoid making large changes at once (the change for a single parameter should not exceed 2 times or ±30% of the original value, whichever is stricter).
            3) Do not change parameters that have been proven to have "no impact" on performance; avoid adjusting parameters that are clearly mutually exclusive.
            4) All changes must meet the requirements for dependencies, mutual exclusions, upper and lower limits, type, and unit.
            5) The recommended value for each parameter must be acceptable to the system and ensure that the application can start.

            6) If no suitable changes are available, output an empty JSON object.
            Output format (must be strictly followed):
            - Output only one JSON object, with the key being the "adjustable parameter name" and the value being the "recommended value."
            - Do not output any additional text, explanations, examples, code blocks, or comments.
            """)

        else:
            prompt = translate(
                f"""
            [{self.service_name}类] 你是专业的系统运维专家。当前性能指标未达预期，且上一轮调优为负向结果（性能下降/不稳定/报错等）。
            请在“心中完成推理”，只输出最终 JSON；除 JSON 以外不要输出任何文字、代码块或注释。

            目标：基于以下信息，总结历史调优经验中的baseline、最佳调优结果、最差调优结果以及previous_result以及参数取值，反向微调上轮可能导致退化的参数，并选择更保守且安全的值；仅给出需要变更的参数与推荐新值。

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
            """,
                f"""
            [{self.service_name}] You are a professional system operations expert. The current performance metrics are not meeting expectations, and the last round of optimization resulted in a negative outcome (performance degradation, instability, errors, etc.).
            Please perform reasoning internally and output only the final JSON; do not output any text, code blocks, or comments other than the JSON.

            Objective: Based on the following information, summarize the baseline, the best and worst optimization results, the previous result, and the parameter values from historical optimization experiences. Reverse-tune the parameters that may have caused degradation in the last round and select more conservative and safe values. Only provide the parameters that need to be changed and the recommended new values.

            Current environment configuration information:
            {self.static_profile}

            Historical optimization information (including modified parameters and results):
            {history_result}

            Optimization approach:
            {optimization_idea}

            The full set of adjustable parameters (including type, range, enumerations, default values, etc.) and the baseline values corresponding to these parameters are:
            {params_set_str}

            Strict rules (must be followed):
            1) Output only the parameters that need to be changed compared to the current configuration; do not output any irrelevant or non-beneficial parameters.
            2) For parameters that were changed in the last round and are suspected to have caused degradation: adjust them in the opposite direction with small steps (usually 30% to 50% of the previous step size, typically -10% to -20%); if necessary, disable optional high-overhead features.
            3) Avoid adjusting too many parameters at once; do not adjust mutually exclusive parameters simultaneously; prefer correction methods with lower risk.
            4) The recommended values must meet the requirements for dependencies, mutual exclusions, upper and lower limits, types, and units.
            5) The recommended value for each parameter must be actually acceptable by the system and ensure that the application can start.
            6) If no suitable changes are available, output an empty JSON object.
            
            Output format (must be strictly followed):
            - Output only one JSON object, with the key being "tunable parameter name" and the value being "recommended value".
            - Do not output any extra text, explanations, examples, code fences, or comments.
            """)
        response = get_llm_response(prompt, max_tokens=1024)
        return response

