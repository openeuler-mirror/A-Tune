from .cpu_collector import CpuCollector, get_cpu_cmd
from .disk_collector import DiskCollector, get_disk_cmd
from .memory_collector import MemoryCollector, get_memory_cmd
from .network_collector import NetworkCollector, get_network_cmd
from .mysql_collector import MysqlCollector, get_mysql_cmd
from .base_collector import CollectorArgs

class MetricCollector:
    def __init__(self, host_ip: str, host_port: int, host_user: str, host_password: str, app: str = None):
        self.args = CollectorArgs(
            host_ip=host_ip,
            host_port=host_port,
            host_user=host_user,
            host_password=host_password,
        )
        self.app = app  # 新增app属性
        self.cpu_collector = CpuCollector(
            cmd = get_cpu_cmd(),
            host_ip=self.args.host_ip,
            host_port=self.args.host_port,
            host_user=self.args.host_user,
            host_password=self.args.host_password
        )
        self.disk_collector = DiskCollector(
            cmd = get_disk_cmd(),
            host_ip=self.args.host_ip,
            host_port=self.args.host_port,
            host_user=self.args.host_user,
            host_password=self.args.host_password
        )
        self.memory_collector = MemoryCollector(
            cmd = get_memory_cmd(),
            host_ip=self.args.host_ip,
            host_port=self.args.host_port,
            host_user=self.args.host_user,
            host_password=self.args.host_password
        )
        self.network_collector = NetworkCollector(
            cmd = get_network_cmd(),
            host_ip=self.args.host_ip,
            host_port=self.args.host_port,
            host_user=self.args.host_user,
            host_password=self.args.host_password
        )
        if self.app.lower() == "mysql":
            self.mysql_collector = MysqlCollector(
                cmd = get_mysql_cmd(
                    host_ip=self.args.host_ip,
                    host_port=self.args.host_port,
                    host_user=self.args.host_user,
                    host_password=self.args.host_password
                ),
                host_ip=self.args.host_ip,
                host_port=self.args.host_port,
                host_user=self.args.host_user,
                host_password=self.args.host_password
            )

    def run(self) -> dict:
        """
        运行所有数据收集器，收集并返回综合结果。
        """
        # 调用每个子收集器的 run 方法
        cpu_data = self.cpu_collector.run()
        disk_data = self.disk_collector.run()
        memory_data = self.memory_collector.run()
        network_data = self.network_collector.run()
        if self.app.lower() == "mysql":
            mysql_data = self.mysql_collector.run()
        else:
            mysql_data = {}

        # 合并所有收集到的数据
        combined_data = {
            "Cpu": cpu_data,
            "Disk": disk_data,
            "Memory": memory_data,
            "Network": network_data,
            "Mysql": mysql_data
        }

        return combined_data

