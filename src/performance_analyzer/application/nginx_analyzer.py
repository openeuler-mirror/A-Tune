from ..base_analyzer import BaseAnalyzer

class NginxAnalyzer(BaseAnalyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def analyze(self) -> str:
        if not self.data:
            return "当前系统没有运行Nginx应用，无需分析Nginx性能。\n"

        # self.data 本身就是结构化后的nginx状态数据
        nginx_status_text = "\n".join([f"{k}: {v}" for k, v in self.data.items()])

        return self.generate_report(nginx_status_text)

    def generate_report(self, nginx_status_text: str) -> str:
        report_prompt = f"""
        # CONTEXT #
        以下是通过 Nginx status 接口获取的运行状态数据：
        {nginx_status_text}

        # OBJECTIVE #
        请根据上述内容简要分析 Nginx 应用的当前运行状态。
        要求：
        1. 不要包含任何优化建议；
        2. 尽量提取关键数据进行解释；
        3. 回答不超过200字。

        # STYLE #
        你是一个资深系统运维工程师，语言简洁、客观、严谨、清晰。

        # TONE #
        严肃、专业。

        # AUDIENCE #
        报告面向其他系统工程师，应真实可信，避免臆测。

        # RESPONSE FORMAT #
        回答以“Nginx分析如下:”开头，逐条列出结论（如有多个点请编号分条）。
        """

        return self.ask_llm(report_prompt) + "\n"
