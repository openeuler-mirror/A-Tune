from .base_analyzer import BaseAnalyzer

class MemoryAnalyzer(BaseAnalyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def analyze(self) -> str:
        report = "基于采集的系统指标，内存初步的性能分析如下：\n"
        swapout, oom_kill, swap_ratio, util = (
            self.data.get("swapout", 0), 
            self.data.get("omm_kill", 0),
            self.data.get("交换空间使用率", 0),
            self.data.get("内存使用率", 0)
        )
        swap_ratio = 1 - swap_ratio
        report += f"系统内存使用率是{util}\n"
        report += self.omm_kill_analysis(oom_kill)
        report += self.swap_analysis(swap_ratio)
        report += self.swapout_analysis(swapout)
        return report
    
    def omm_kill_analysis(
        self,
        oom_kill: float,
) -> str:
        return self.generate_report_line(oom_kill == 1, "系统近期发生过oom_kill行为, 即内存严重不足，需要杀死进程来释放内存")
    
    def swap_analysis(
        self,
        swap_low: float,
    ) -> str:
        return self.generate_report_line(swap_low < 0.1, f"系统可用交换空间百分比为{swap_low},低于预设阈值, 系统可能很快会耗尽虚拟内存，需要减少运行程序的数量和大小或增加交换空间来避免完全耗尽")
    
    def swapout_analysis(
        self,
        swapout: float,
    ) -> str:
        return self.generate_report_line(swapout == 1, "系统持续以高速率将页面交换到交换空间，这表明系统物理可能内存不足")
    
    def generate_report(
        self,
        memory_report: str
    ) -> str:
        # TO DO
        # 要有一个报告模板，指明包含哪些信息，以及报告格式
        report_prompt = f"""
        以下内容是linux系统中内存相关的性能信息:
        {memory_report}
        信息中所涉及到的数据准确无误,真实可信。

        # OBJECTIVE #
        请根据上述信息,分析系统内存的性能状况。
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
        回答以"内存分析如下:"开头，然后另起一行逐条分析。
        如果有多条分析结论，请用数字编号分点作答。
        
        """
        return self.ask_llm(report_prompt) + "\n"