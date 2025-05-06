from .base_analyzer import BaseAnalyzer

class NetworkAnalyzer(BaseAnalyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def analyze(self) -> str:
        report = "基于采集的系统指标, 网络初步的性能分析如下：\n"
        listenOverflows, fulldocookies, fulldrop, network_adapter = (
            self.data.get("listenOverflows", 0), 
            self.data.get("fulldocookies", 0),
            self.data.get("fulldrop", 0),
            self.data.get("网卡指标", "")
        )
        report += self.listenOverflows_analysis(listenOverflows)
        report += self.fulldocookies_analysis(fulldocookies)
        report += self.fulldrop_analysis(fulldrop)
        report += self.network_adapter_analysis(network_adapter)
        return report
    
    def listenOverflows_analysis(
        self,
        listenOverflows: float
    ) -> str:
        return self.generate_report_line(listenOverflows == 1, "系统存在因为监听队列回滚而丢弃TCP连接的现象。这通常表明系统无法及时处理传入的连接请求, 导致连接被系统自动丢弃")

    def fulldrop_analysis(
        self,
        fulldrop: float
    ) -> str:
        return self.generate_report_line(fulldrop == 1, "系统存在因为TCP请求队列满了而丢弃新的连接请求的现象。这通常表明系统无法及时处理传入的连接请求, 导致内核自动丢弃这些请求")

    def fulldocookies_analysis(
        self,
        fulldocookies: float
    ) -> str:
        return self.generate_report_line(fulldocookies == 1, "系统存在因为TCP请求队列满了而发送SYN COOKIE的现象。这通常表明系统无法及时处理传入的连接请求, 导致内核自动采取措施来处理这些请求, 例如发送SYN COOKIE")

    def network_adapter_analysis(
        self,
        network_adapter: str
    ) -> str:
        network_adapter_prompt = f"""
        # CONTEXT # 
        当前有linux系统网卡的数据,性能指标是在linux系统中执行 netstat -i 获得的输出，内容如下：
        {network_adapter}

        # OBJECTIVE #
        请根据这些性能指标,生成一份逻辑清晰、条理清楚的系统网卡的性能总结报告。
        要求：
        1.答案中只分析可能对系统性能产生影响的指标数据。
        2.答案中不要包含任何优化建议。
        3.答案中尽可能保留信息中真实有效的数据。
        4.答案不超过200字。

        # STYLE #
        你是一个专业的系统运维专家,你的回答应该逻辑严谨、表述客观、简洁易懂、条理清晰，让你的回答真实可信

        # Tone #
        你应该尽可能秉承严肃、认真、严谨的态度

        # AUDIENCE #
        你的答案将会是其他系统运维专家的重要参考意见，请尽可能提供真实有用的信息，不要胡编乱造。

        # RESPONSE FORMAT #
        如果有多条分析结论，请用数字编号分点作答。

        """
        return self.ask_llm(network_adapter_prompt)
    
    def generate_report(
        self,
        network_report: str
    ) -> str:
        # TO DO
        # 要有一个报告模板，指明包含哪些信息，以及报告格式
        report_prompt = f"""
        以下内容是linux系统中网络传输相关的性能信息:
        {network_report}
        信息中所涉及到的数据准确无误,真实可信。

        # OBJECTIVE #
        请根据上述信息,分析系统网络传输的性能状况。
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
        回答以"网络分析如下:"开头，然后另起一行逐条分析。
        如果有多条分析结论，请用数字编号分点作答。
        
        """
        return self.ask_llm(report_prompt) + "\n"