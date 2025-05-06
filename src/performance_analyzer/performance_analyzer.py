from .cpu_analyzer import CpuAnalyzer
from .disk_analyzer import DiskAnalyzer
from .memory_analyzer import MemoryAnalyzer
from .network_analyzer import NetworkAnalyzer
from .mysql_analyzer import MysqlAnalyzer
from .base_analyzer import BaseAnalyzer
from typing import Tuple

class PerformanceAnalyzer(BaseAnalyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cpu_analyzer = CpuAnalyzer(data=self.data.get("Cpu", {}))
        self.disk_analyzer = DiskAnalyzer(data=self.data.get("Disk", {}))
        self.memory_analyzer = MemoryAnalyzer(data=self.data.get("Memory", {}))
        self.network_analyzer = NetworkAnalyzer(data=self.data.get("Network", {}))
        self.mysql_analyzer = MysqlAnalyzer(data=self.data.get("Mysql", {}))
    
    def analyze(
        self,
        report: str
    ) -> str:
        bottle_neck_prompt = f"""
        # CONTEXT # 
        当前linux系统的性能分析报告如下,报告中所涉及到的数据准确无误,真实可信:
        {report}

        # OBJECTIVE #
        请根据系统性能分析报告,确定当前系统是否存在性能瓶颈;如果存在性能瓶颈,则该瓶颈主要是存在于系统的哪个方面。
        你应该依据多条信息和多个指标的数据进行综合判断,不要基于单点信息轻易下结论,你最终的结论应该能找到多个佐证。
        要求：
        1.你必须从[CPU,NETWORK,DISK,MEMORY,NONE]这五个选项中选择一项作为你的答案。
        2.不要回答多余的文字，你的答案必须严格和上述选项描述一致。
        3.如果你认为没有性能瓶颈,请选择NONE。

        # STYLE #
        你是一个专业的系统运维专家,你只用回答上述五个选项之一

        # Tone #
        你应该尽可能秉承严肃、认真、严谨的态度

        # AUDIENCE #
        你的答案将会是其他系统运维专家的重要参考意见，请认真思考后给出你的答案。

        # RESPONSE FORMAT #
        请直接回答五个选项之一,不要包含多余文字

        """
        result = self.ask_llm(bottle_neck_prompt)
        bottlenecks = {
            "cpu": "CPU",
            "disk": "DISK",
            "network": "NETWORK",
            "memory": "MEMORY",
            "none": "NONE"
        }
        
        # 转换为小写并查找瓶颈
        for key, value in bottlenecks.items():
            if key in result.lower():
                return value
        
        # 如果没有找到明确的瓶颈，返回UNKNOWN BOTTLENECKS
        return "UNKNOWN BOTTLENECKS" 

    def generate_report(self) -> Tuple[str, str]:
        os_performance_report = ""
        os_performance_report += self.cpu_analyzer.run()
        os_performance_report += self.disk_analyzer.run()
        os_performance_report += self.memory_analyzer.run()
        os_performance_report += self.network_analyzer.run()
        app_performance_report = ""
        app_performance_report += self.mysql_analyzer.run()
        return os_performance_report, app_performance_report
    
    def run(self) -> Tuple[str, str]:
        os_performance_report, app_performance_report = self.generate_report()
        bottleneck = self.analyze(os_performance_report)
        return os_performance_report + app_performance_report, bottleneck