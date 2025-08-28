from src.performance_analyzer.base_analyzer import BaseAnalyzer


class AppAnalyzer(BaseAnalyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def analyze(self) -> str:
        if not self.data:
            return f"当前系统没有运行{self.app}应用，无需分析ceph性能。\n"
        report = f"基于采集的系统指标, {self.app}初步的性能分析如下:\n"
        for cmd, result in self.data.items():
            profile_prompt = f"""
                # CONTEXT # 
                以下内容是linux命令<{cmd}>的输出：
                {result}

                # OBJECTIVE #
                请根据上述信息,简要分析{self.app}应用的性能状况。
                要求：
                1.答案不超过200字。
                2.答案中不要包含任何优化建议。
                3.答案中尽可能保留信息中真实有效的数据。

                # STYLE #
                你是一个专业的系统运维专家,你的回答应该逻辑严谨、表述客观、简洁易懂、条理清晰，让你的回答真实可信

                # Tone #
                你应该尽可能秉承严肃、认真、严谨的态度

                # AUDIENCE #
                你的答案将会是其他系统运维专家的重要参考意见，请尽可能提供真实有用的信息，不要胡编乱造。

                # RESPONSE FORMAT #
                如果有多条分析结论，请用数字编号分点作答。

                """
            report += self.ask_llm(profile_prompt)

        return report

    def generate_report(
            self,
            app_report: str
    ) -> str:
        # TO DO
        # 要有一个报告模板，指明包含哪些信息，以及报告格式
        if app_report == "当前系统没有运行ceph应用，无需分析ceph性能。\n":
            return app_report
        report_prompt = f"""
        # CONTEXT # 
        linux系统中正在运行{self.app}应用, 以下内容是{self.app}相关的性能信息:
        {app_report}
        信息中所涉及到的数据准确无误,真实可信。

        # OBJECTIVE #
        请根据上述信息,分析{self.app}应用的性能状况。
        要求：
        1.答案中不要包含任何优化建议。
        2.答案中尽可能保留信息中真实有效的数据。
        3.不要遗漏任何值得分析的信息。

        # STYLE #
        你是一个专业的系统运维专家,你的回答应该逻辑严谨、表述客观、简洁易懂、条理清晰，让你的回答真实可信

        # Tone #
        你应该尽可能秉承严肃、认真、严谨的态度

        # AUDIENCE #
        你的答案将会是其他系统运维专家的重要参考意见，请尽可能提供真实有用的信息，不要胡编乱造。

        # RESPONSE FORMAT #
        回答以"{self.app}分析如下:"开头，然后另起一行逐条分析。
        如果有多条分析结论，请用数字编号分点作答。

        """
        return self.ask_llm(report_prompt) + "\n"
