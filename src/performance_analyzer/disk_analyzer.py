from .base_analyzer import BaseAnalyzer

class DiskAnalyzer(BaseAnalyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def analyze(self) -> str:
        report = "基于采集的系统指标, 磁盘初步的性能分析报告如下: \n"
        disks_info, iowait = self.data.get("磁盘信息", {})[0], self.data.get("iowait", 0)
        report += f"系统iowait的值是{iowait}\n"
        for disk_name, disk_info in disks_info.items():
            wait_time, queue_lenth, util, read_speed, write_speed, read_size, write_size = (
                disk_info.get("磁盘平均等待时间变化趋势", 0),
                disk_info.get("磁盘平均请求队列长度变化趋势", 0),
                disk_info.get("磁盘利用率", 0),
                disk_info.get("单位时间读速率", 0),
                disk_info.get("单位时间写速率", 0),
                disk_info.get("单位时间读大小", 0),
                disk_info.get("单位时间写大小", 0),
            )
            report += f"磁盘{disk_name}的基本信息如下：\n"
            report += f"磁盘利用率是{util}，磁盘读速率是{read_speed}，磁盘写速率是{write_speed}\n"
            report += self.disk_info_analysis(wait_time, queue_lenth, util)
            report += self.disk_rw_analysis(read_speed, write_speed, read_size, write_size, util)
        return report
    
    def disk_info_analysis(
        self,
        wait_time: float,
        queue_lenth: float,
        util: float,
    ) -> str:
        disk_info_report = ""
        queue_lenth_message = (
            "该磁盘设备请求队列的长度在增加，且设备利用率超过预设阈值，这可能表明该磁盘正在接近或达到其处理能力的极限"
            if queue_lenth > 0 and util > 0.90
            else ""
        )
        disk_info_report += self.generate_report_line(queue_lenth_message, queue_lenth_message)

        wait_time_message = (
            "该磁盘设备请求处理速度在下降，且设备利用率超过预设阈值, 这可能表明该磁盘正在接近或达到其处理能力的极限"
            if wait_time > 0 and util > 0.90
            else ""
        )
        disk_info_report += self.generate_report_line(wait_time_message, wait_time_message)
        return disk_info_report

    def disk_rw_analysis(
        self,
        read_speed: float,
        write_speed: float,
        read_size: float,
        write_size: float,
        util: float,
    ) -> str:
        disk_rw_report = ""
        read_size = read_size/1024
        write_size= write_size/1024

        iops_message = (
            "该磁盘平均 Input/Ouput Operations Per Second (IOPS) 操作数超过预设限制，且设备利用率超过预设阈值, 这可能表明该磁盘正在接近或达到其处理能力的极限"
            if read_speed + write_speed > 120 and util > 0.90
            else ""
        )
        disk_rw_report += self.generate_report_line(iops_message, iops_message)

        size_message = (
            "该磁盘的平均传输速率超过预设带宽限制，且设备利用率超过预设阈值，这可能表明该磁盘正在接近或达到其处理能力的极限"
            if read_size + write_size > 100 and util > 0.90
            else ""
        )
        disk_rw_report += self.generate_report_line(size_message, size_message)

        return disk_rw_report
    
    def generate_report(
        self,
        disk_report: str
    ) -> str:
        # TO DO
        # 要有一个报告模板，指明包含哪些信息，以及报告格式
        report_prompt = f"""
        以下内容是linux系统中磁盘相关的性能信息:
        {disk_report}
        信息中所涉及到的数据准确无误,真实可信。

        # OBJECTIVE #
        请根据上述信息,分析系统磁盘的性能状况。
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
        回答以"磁盘分析如下:"开头，然后另起一行逐条分析。
        如果有多条分析结论，请用数字编号分点作答。
        
        """
        return self.ask_llm(report_prompt) + "\n"
