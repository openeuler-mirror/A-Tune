from .base_analyzer import BaseAnalyzer

class CpuAnalyzer(BaseAnalyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def analyze(self) -> str:
        report = "基于采集的系统指标, CPU初步的性能分析如下:\n"
        avg_load_report = self.avg_load_analysis()
        cpu_info_report = self.cpu_info_analysis()
        pid_info_report = self.pid_info_analysis()

        report += avg_load_report
        report += cpu_info_report
        report += pid_info_report

        return report

    def avg_load_analysis(self) -> str:
        avg_load_analysis_report = ""

        # 提取cpu平均负载数据
        one_min, five_min, ten_min = self.data.get("1min", 0.0), self.data.get("5min", 0.0), self.data.get("10min", 0.0)

        # 生成平均负载数据
        avg_load_analysis_report += f"当前系统1分钟平均负载是{one_min}, 5分钟平均负载是{five_min}, 10分钟平均负载是{ten_min}\n"

        # 生成报告
        avg_load_analysis_report += (
            self.generate_report_line(one_min > 1, "过去1分钟系统负载过重,系统可能存在cpu性能瓶颈")
        )
        avg_load_analysis_report += (
            self.generate_report_line(five_min > 1, "过去5分钟系统负载过重,系统可能存在cpu性能瓶颈")
        )
        avg_load_analysis_report += (
            self.generate_report_line(ten_min > 1, "过去10分钟系统负载过重,系统可能存在cpu性能瓶颈")
        )

        # 检查负载是否突然增加
        sudden_increase_message = (
            "过去1分钟系统负载突然迅速增加，系统对cpu性能要求可能会变高"
            if (one_min > 2 * five_min or one_min > 2 * ten_min) and one_min > 1
            else ""
        )
        avg_load_analysis_report += self.generate_report_line(sudden_increase_message, sudden_increase_message)

        # 检查负载稳定性
        stability_message = (
            "过去10分钟内系统负载较稳定，无明显波动"
            if abs(one_min - five_min) <= 0.2 and abs(one_min - ten_min) <= 0.2 and abs(five_min - ten_min) <= 0.2
            else "过去10分钟内系统负载存在一定变化波动"
        )
        avg_load_analysis_report += self.generate_report_line(stability_message, stability_message)

        # 检查负载上升趋势
        trend_message = (
            "过去10分钟内系统负载呈不断上升趋势，系统对cpu性能要求可能会变高"
            if one_min - five_min > 0.2 and five_min - ten_min > 0.2 and one_min > 0.5
            else ""
        )
        avg_load_analysis_report += self.generate_report_line(trend_message, trend_message)

        return avg_load_analysis_report
    
    def cpu_info_analysis(self) -> str:
        cpu_info_analysis_report = ""

        # 提取CPU信息数据
        usr, sys, irq, soft, util = (
            self.data.get("用户态中的cpu利用率", 0),
            self.data.get("kernel内核态执行时的CPU利用率", 0),
            self.data.get("硬中断占用CPU时间的百分比", 0),
            self.data.get("软中断占用CPU时间的百分比", 0),
            self.data.get("CPU利用率", 0)
        )
        block_process, cpu_load, io_load = (
            self.data.get("阻塞进程率", 0),
            self.data.get("计算密集型", 0),
            self.data.get("IO密集型", 0)
        )
        context_switch, sys_call, cpu_num = (
            self.data.get("系统每秒进行上下文切换的次数", 0),
            self.data.get("系统单位时间调用次数", 0),
            self.data.get("cpu核数", 1)  # 默认为1，避免除以0
        )

        # 构建基本信息报告
        cpu_info_analysis_report += (
            f"当前系统中, 用户态CPU利用率: {usr}%, 内核态CPU利用率: {sys}%, "
            f"硬中断占比: {irq}%, 软中断占比: {soft}%, CPU总体利用率: {util}%\n"
        )

        # 根据条件生成其他报告行
        conditions_and_messages = [
            (usr + sys + irq + soft > 0.9, "当前系统负载较高, 可能存在CPU瓶颈。"),
            (cpu_load == 1, "系统用户态CPU利用率远大于内核态CPU利用率, 表明系统上的应用程序正在大量使用CPU资源, 是计算密集型负载场景。"),
            (io_load == 1, "系统内核代码调用频率很高, 符合I/O密集型负载场景的特征。"),
            (context_switch > cpu_num * 4000, f"系统每秒发生的上下文切换次数是{context_switch}，已超出正常阈值上限，会对系统性能产生劣化影响。"),
            (sys_call > cpu_num * 10000, f"每秒系统调用次数是{sys_call}，表明有大量的系统调用正在发生，可能是由高负载或资源密集型应用程序引起的。"),
            ((usr + sys) > 0.7 and sys > (0.75 * usr + 0.75 * sys), "在系统模式下的处理能力可能不足，系统可能无法有效地处理所有传入的系统调用，可能导致响应时间变长或系统性能下降。"),
            (sys_call < 100 and util > 0.5, "系统当前有大量浮点异常(FPEs)进程。"),
        ]

        for condition, message in conditions_and_messages:
            cpu_info_analysis_report += self.generate_report_line(condition, message)

        # 添加阻塞进程报告
        cpu_info_analysis_report += f"处于阻塞状态的进程占比是{block_process}%\n"

        return cpu_info_analysis_report
    
    def pid_info_analysis(self) -> str:
        pid_info_report = "基于采集的系统指标，系统进程初步的性能分析如下：\n"
        pid_prompt = """
        # CONTEXT # 
        当前有linux系统进程的数据,性能指标是在linux系统中执行 pidstat -d | head -6 获得的输出，内容如下：
        {pid_info}

        # OBJECTIVE #
        请根据这些性能指标,生成一份逻辑清晰、条理清楚的系统进程的性能总结报告。
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
        pid_info = self.data["进程信息"]
        pid_info_report += self.ask_llm(pid_prompt.format(pid_info=pid_info))
        return pid_info_report
    
    def generate_report(
        self,
        cpu_report: str
    ) -> str:
        # TO DO
        # 要有一个报告模板，指明包含哪些信息，以及报告格式
        report_prompt = f"""
        以下内容是linux系统中cpu相关的性能信息:
        {cpu_report}
        信息中所涉及到的数据准确无误,真实可信。

        # OBJECTIVE #
        请根据上述信息,分析系统cpu的性能状况。
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
        回答以"CPU分析如下:"开头，然后另起一行逐条分析。
        如果有多条分析结论，请用数字编号分点作答。
        
        """
        return self.ask_llm(report_prompt) + "\n"