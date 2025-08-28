import logging

from .cpu_collector import CpuCollector, get_cpu_cmd
from .disk_collector import DiskCollector, get_disk_cmd
from .memory_collector import MemoryCollector, get_memory_cmd
from .network_collector import NetworkCollector, get_network_cmd
from .base_collector import CollectorArgs

from src.utils.shell_execute import SshClient
from src.performance_collector.app_collector import AppCollector
from src.utils.collector.collector_trigger import TriggerEventListener, TriggerStatus


triggered_event_listener = TriggerEventListener()


class MetricCollector:

    def __init__(
        self,
        ssh_client: SshClient,
        app: str = None,
        pressure_test_mode: bool = False,
    ):
        self.args = CollectorArgs(
            ssh_client=ssh_client
        )
        self.app = app  # 新增app属性
        self.pressure_test_mode = pressure_test_mode
        self.cpu_collector = CpuCollector(
            cmd=get_cpu_cmd(),
            ssh_client=self.args.ssh_client,
        )
        self.disk_collector = DiskCollector(
            cmd=get_disk_cmd(),
            ssh_client=self.args.ssh_client,
        )
        self.memory_collector = MemoryCollector(
            cmd=get_memory_cmd(),
            ssh_client=self.args.ssh_client,
        )
        self.network_collector = NetworkCollector(
            cmd=get_network_cmd(),
            ssh_client=self.args.ssh_client,
        )
        self.app_collector = AppCollector(
            ssh_client=ssh_client,
            app=app,
        )

    def run(self) -> dict:
        """
        运行所有数据收集器，收集并返回综合结果。
        """
        logging.info("[MetricCollector] collecting workload metrics ...")
        # 全局触发模式，如果需要一边模拟压测一边采集数据时开启，阻塞程序直到可以开始采集数据
        if self.pressure_test_mode:
            logging.info("[MetricCollector] waiting for pressure test initializing ...")
            event_status = triggered_event_listener.wait()

            if event_status == TriggerStatus.CLOSE:
                raise RuntimeError(
                    f"[MetricCollector] waiting for trigger signale timeout, skip tasks"
                )
        # 调用每个子收集器的 run 方法
        cpu_data = self.cpu_collector.run()
        disk_data = self.disk_collector.run()
        memory_data = self.memory_collector.run()
        network_data = self.network_collector.run()
        app_data = self.app_collector.run()

        # 合并所有收集到的数据
        combined_data = {
            "Cpu": cpu_data,
            "Disk": disk_data,
            "Memory": memory_data,
            "Network": network_data,
            "Application": app_data,
        }

        return combined_data
