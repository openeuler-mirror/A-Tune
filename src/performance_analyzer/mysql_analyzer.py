from .base_analyzer import BaseAnalyzer

class MysqlAnalyzer(BaseAnalyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def analyze(self) -> str:
        if not self.data:
            return "当前系统没有运行MySQL应用，无需分析MySQL性能。\n"
        report = "基于采集的系统指标, MySQL初步的性能分析如下:\n"
        for k,v in self.data.items():
            if k == "profiling":
                report += self.profiling_analysis(v)
                continue
            if k == "processlist":
                report += self.processlist_analysis(v)
                continue
            report += f"{k}的值是{v}\n"

        return report
    
    def profiling_analysis(
        self,
        stdout
    ) -> str:
        profile_prompt = """
        # CONTEXT # 
        以下内容是linux命令<mysql -e "SHOW PROFILES">的输出：
        {content}

        # OBJECTIVE #
        请根据上述信息,简要分析mysql应用的性能状况。
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
        return self.ask_llm(profile_prompt.format(content=stdout))
    
    def processlist_analysis(
        self,
        stdout
    ) -> str:
        processlist_prompt = """
        # CONTEXT # 
        以下内容是linux命令<mysql -e "SHOW PROCESSLIST">的输出：
        {content}

        # OBJECTIVE #
        请根据上述信息,简要分析mysql应用的性能状况。
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
        return self.ask_llm(processlist_prompt.format(content=stdout))
    
    def generate_report(
        self,
        mysql_report: str
    ) -> str:
        # TO DO
        # 要有一个报告模板，指明包含哪些信息，以及报告格式
        if mysql_report == "当前系统没有运行MySQL应用，无需分析MySQL性能。\n":
            return mysql_report
        report_prompt = f"""
        # CONTEXT # 
        linux系统中正在运行MySQL应用, 以下内容是MySQL相关的性能信息:
        {mysql_report}
        信息中所涉及到的数据准确无误,真实可信。

        # OBJECTIVE #
        请根据上述信息,分析mysql应用的性能状况。
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
        回答以"MySQL分析如下:"开头，然后另起一行逐条分析。
        如果有多条分析结论，请用数字编号分点作答。
        
        """
        return self.ask_llm(report_prompt) + "\n"