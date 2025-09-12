import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from src.utils.shell_execute import SshClient


class COLLECTMODE:
    DIRECT_MODE = 0
    ATTACH_MODE = 1


class BaseCollector(ABC):
    """性能数据收集器基类"""

    def __init__(self):
        self.raw_data: Dict[str, float] = {}
        self.processed_data: Dict[str, float] = {}
        self.collect_cmd: str = ""

    @abstractmethod
    def collect(self):
        """收集性能数据"""
        pass

    @abstractmethod
    def process(self):
        """处理原始数据"""
        pass

    @staticmethod
    def is_number(s: str) -> bool:
        """检查字符串是否为数字"""
        try:
            float(s)
            return True
        except ValueError:
            return False


class PerfCollector(BaseCollector):
    """基于perf的性能数据收集器"""

    # 性能事件配置
    PMU_CONFIGS = {
        "topdown": {
            'r0011': "cycle",
            'r2014': "fetch_bubble",
            'r201d': "fetch_bubble_max",
            'r001b': "inst_spec",
            'r0008': "inst_retired",
            'r7001': "execstall_cycle",
            'r7003': "fsustall",
            'r7004': "memstall_anyload",
            'r7005': "memstall_anystore",
            'r7006': "memstall_l1miss",
            'r7007': "memstall_l2miss",
            'r0010': "brmisspred",
            'r2013': "o3flush",
            'context-switches': "context_switches",
            'cpu-migrations': "cpu_migrations",
            'page-faults': "page_faults",
        },
        "cache": {
            'r0001': 'l1i_refill',
            'r0014': 'l1i_access',
            'r0003': 'l1d_refill',
            'r0004': 'l1d_access',
            'r0028': 'l2i_refill',
            'r0027': 'l2i_access',
            'r0017': 'l2d_refill',
            'r0016': 'l2d_access',
            'r0008': 'inst_retired',
        },
        "branch": {
            'r0011': 'cycle',
            'r200b': 'alu_isq_stall',
            'r200c': 'lsu_isq_stall',
            'r200d': 'fsu_isq_stall',
            'r0010': 'brmisspred',
            'r0012': 'brpred',
        },
        "tlb": {
            'r0002': 'l1i_tlb_refill',
            'r0026': 'l1i_tlb',
            'r0005': 'l1d_tlb_refill',
            'r0025': 'l1d_tlb',
            'r002e': 'l2i_tlb_refill',
            'r0030': 'l2i_tlb',
            'r002d': 'l2d_tlb_refill',
            'r002f': 'l2d_tlb',
            'r0035': 'itlb_walk',
            'r0034': 'dtlb_walk',
            'r0008': 'inst_retired',
            'r0011': 'cycle',
            'r7002': 'divstall',
        }
    }

    # 微架构配置
    FW_CONFIG = {'dispatch_size': 4}

    def __init__(
            self,
            config_type: str,
            ssh_client: SshClient = None,
            duration: float = 0.1,
            target_pid: int = 0
    ):
        super().__init__()
        self.ssh_client = ssh_client
        self.config_type = config_type
        self.cfg_pmu = self.PMU_CONFIGS.get(config_type, {})
        self.duration = duration
        self.target_pid = target_pid

    def set_collector_param(
            self,
            ssh_client: SshClient,
            duration: float = 0.1,
            target_pid: int = 0
    ):
        """设置收集器参数"""
        self.ssh_client = ssh_client
        self.duration = duration
        self.target_pid = target_pid
        self._generate_collect_command()

    def _generate_collect_command(self):
        """生成perf收集命令"""
        events = ",".join(self.cfg_pmu.keys())
        target = f"-p {self.target_pid}" if self.target_pid else "-a"
        self.collect_cmd = f"perf stat -e {events} {target} sleep {self.duration}"
        logging.debug(f"Generated perf command: {self.collect_cmd}")

    def collect(self):
        """收集性能数据"""
        if not self.ssh_client:
            raise RuntimeError("Host information not set")
        result = self.ssh_client.run_cmd(self.collect_cmd)
        self._parse_perf_output(result.err_msg)

    def _parse_perf_output(self, output: str):
        """解析perf输出"""
        for line in output.splitlines():
            line = line.rstrip()
            if not line:
                continue

            parts = line.split()
            if len(parts) < 2:
                continue

            value = parts[0].replace(',', '')
            event_name = parts[1]

            # 处理未计数的事件
            if value == "<not":
                logging.error(f"Event not counted: {line}")
                self._store_event(event_name, 0)
                continue

            if self.is_number(value):
                self._store_event(event_name, float(value))

    def _store_event(self, event_name: str, value: float):
        """存储性能事件数据"""
        if event_name in self.cfg_pmu:
            metric_name = self.cfg_pmu[event_name]
            current = self.raw_data.get(metric_name, 0.0)
            self.raw_data[metric_name] = current + value


class TopDownCollector(PerfCollector):
    """TopDown性能分析收集器"""

    def __init__(
            self,
            ssh_client: Optional[SshClient] = None,
            duration: float = 0.1,
            target_pid: int = 0
    ):
        super().__init__("topdown", ssh_client, duration, target_pid)

    def process(self):
        """处理TopDown性能数据"""
        # 提取微架构参数
        try:
            dispatch_size = self.FW_CONFIG["dispatch_size"]

            # 计算各级指标
            cycle = self.raw_data["cycle"]
            inst_retired = self.raw_data["inst_retired"]
            execstall_cycle = self.raw_data["execstall_cycle"]

            # L1 指标
            self.processed_data['frontend_bound'] = self.raw_data['fetch_bubble'] / (dispatch_size * cycle) * 100
            self.processed_data['bad_spec'] = (self.raw_data['inst_spec'] - inst_retired) / (
                    dispatch_size * cycle) * 100
            self.processed_data['retiring'] = inst_retired / (dispatch_size * cycle) * 100
            self.processed_data['backend_bound'] = 100 - sum([
                self.processed_data['frontend_bound'],
                self.processed_data['bad_spec'],
                self.processed_data['retiring']
            ])

            # L2 指标
            self.processed_data['frontend_latency_bound'] = self.raw_data['fetch_bubble_max'] / cycle * 100
            self.processed_data['frontend_bandwidth_bound'] = self.processed_data['frontend_bound'] - \
                                                              self.processed_data[
                                                                  'frontend_latency_bound']

            mispred = self.raw_data['brmisspred']
            o3flush = self.raw_data['o3flush']
            self.processed_data['bs_mispred'] = self.processed_data['bad_spec'] * mispred / (mispred + o3flush)
            self.processed_data['bs_mclear'] = self.processed_data['bad_spec'] - self.processed_data['bs_mispred']

            memstall_anyload = self.raw_data['memstall_anyload']
            memstall_anystore = self.raw_data['memstall_anystore']
            self.processed_data['core_bound'] = (
                                                        execstall_cycle - memstall_anyload - memstall_anystore) / execstall_cycle * \
                                                self.processed_data['backend_bound']
            self.processed_data['mem_bound'] = (memstall_anyload + memstall_anystore) / execstall_cycle * \
                                               self.processed_data['backend_bound']

            # L3 指标
            self.processed_data['core_fsu_bound'] = self.raw_data['fsustall'] / cycle * 100
            self.processed_data['core_other_bound'] = self.processed_data['core_bound'] - self.processed_data[
                'core_fsu_bound']

            memstall_l1miss = self.raw_data['memstall_l1miss']
            memstall_l2miss = self.raw_data['memstall_l2miss']
            self.processed_data['mem_l1_bound'] = (memstall_anyload - memstall_l1miss) / execstall_cycle * \
                                                  self.processed_data['backend_bound']
            self.processed_data['mem_l2_bound'] = (memstall_anyload - memstall_l2miss) / execstall_cycle * \
                                                  self.processed_data['backend_bound']
            self.processed_data['mem_l3_dram_bound'] = memstall_l2miss / execstall_cycle * self.processed_data[
                'backend_bound']
            self.processed_data['mem_store_bound'] = memstall_anystore / execstall_cycle * self.processed_data[
                'backend_bound']

            # 系统指标
            self.processed_data['context_switches'] = self.raw_data['context_switches']
            self.processed_data['cpu_migrations'] = self.raw_data['cpu_migrations']
            self.processed_data['page_faults'] = self.raw_data['page_faults']
        except Exception as e:
            return


class CacheCollector(PerfCollector):
    """缓存性能收集器"""

    def __init__(
            self,
            ssh_client: Optional[SshClient] = None,
            duration: float = 0.1,
            target_pid: int = 0
    ):
        super().__init__("cache", ssh_client, duration, target_pid)

    def process(self):
        """处理缓存性能数据"""
        try:
            inst_retired = self.raw_data['inst_retired']

            # 计算各级缓存指标
            self.processed_data['l1i_missrate'] = self.raw_data['l1i_refill'] / self.raw_data['l1i_access'] * 100
            self.processed_data['l1d_missrate'] = self.raw_data['l1d_refill'] / self.raw_data['l1d_access'] * 100

            self.processed_data['l2i_missrate'] = self.raw_data['l2i_refill'] / self.raw_data['l2i_access'] * 100
            self.processed_data['l2d_missrate'] = self.raw_data['l2d_refill'] / self.raw_data['l2d_access'] * 100

            self.processed_data['l1i_mpki'] = self.raw_data['l1i_refill'] / inst_retired * 1000
            self.processed_data['l1d_mpki'] = self.raw_data['l1d_refill'] / inst_retired * 1000

            self.processed_data['l2i_mpki'] = self.raw_data['l2i_refill'] / inst_retired * 1000
            self.processed_data['l2d_mpki'] = self.raw_data['l2d_refill'] / inst_retired * 1000
        except Exception as e:
            return


class BranchCollector(PerfCollector):
    """分支预测性能收集器"""

    def __init__(
            self,
            ssh_client: Optional[SshClient] = None,
            duration: float = 0.1,
            target_pid: int = 0
    ):
        super().__init__("branch", ssh_client, duration, target_pid)

    def process(self):
        """处理分支预测性能数据"""
        try:
            cycle = self.raw_data['cycle']
            brmisspred = self.raw_data['brmisspred']
            brpred = self.raw_data['brpred']

            # 分支预测相关指标
            self.processed_data['branch_missrate'] = brmisspred / (brmisspred + brpred) * 100
            self.processed_data['alu_isq_stall'] = self.raw_data['alu_isq_stall'] / cycle * 100
            self.processed_data['lsu_isq_stall'] = self.raw_data['lsu_isq_stall'] / cycle * 100
            self.processed_data['fsu_isq_stall'] = self.raw_data['fsu_isq_stall'] / cycle * 100
        except Exception as e:
            return


class TlbCollector(PerfCollector):
    """TLB性能收集器"""

    def __init__(
            self,
            ssh_client: Optional[SshClient] = None,
            duration: float = 0.1,
            target_pid: int = 0
    ):
        super().__init__("tlb", ssh_client, duration, target_pid)

    def process(self):
        """处理TLB性能数据"""
        try:
            inst_retired = self.raw_data['inst_retired']
            cycle = self.raw_data['cycle']

            # TLB相关指标
            self.processed_data['l1i_tlb_missrate'] = self.raw_data['l1i_tlb_refill'] / self.raw_data['l1i_tlb'] * 100
            self.processed_data['l1d_tlb_missrate'] = self.raw_data['l1d_tlb_refill'] / self.raw_data['l1d_tlb'] * 100

            self.processed_data['l2i_tlb_missrate'] = self.raw_data['l2i_tlb_refill'] / self.raw_data['l2i_tlb'] * 100
            self.processed_data['l2d_tlb_missrate'] = self.raw_data['l2d_tlb_refill'] / self.raw_data['l2d_tlb'] * 100

            self.processed_data['itlb_walk_rate'] = self.raw_data['itlb_walk'] / self.raw_data['l1i_tlb'] * 100
            self.processed_data['dtlb_walk_rate'] = self.raw_data['dtlb_walk'] / self.raw_data['l1d_tlb'] * 100

            self.processed_data['l1i_tlb_mpki'] = self.raw_data['l1i_tlb_refill'] / inst_retired * 1000
            self.processed_data['l1d_tlb_mpki'] = self.raw_data['l1d_tlb_refill'] / inst_retired * 1000

            self.processed_data['l2i_tlb_mpki'] = self.raw_data['l2i_tlb_refill'] / inst_retired * 1000
            self.processed_data['l2d_tlb_mpki'] = self.raw_data['l2d_tlb_refill'] / inst_retired * 1000

            self.processed_data['itlb_walk_mpki'] = self.raw_data['itlb_walk'] / inst_retired * 1000
            self.processed_data['dtlb_walk_mpki'] = self.raw_data['dtlb_walk'] / inst_retired * 1000

            self.processed_data['div_stall'] = self.raw_data['divstall'] / cycle * 100
        except Exception as e:
            return


class MicroDepCollector:
    """微架构依赖分析主控制器"""

    def __init__(
            self,
            ssh_client: SshClient,
            target_process_name: str = "",
            iteration: int = 1000,
            duration: float = 0.1,
            benchmark_cmd: str = "",
            mode: int = COLLECTMODE.DIRECT_MODE
    ):
        self.ssh_client = ssh_client
        self.target_process_name = target_process_name
        self.max_iteration = iteration
        self.duration = duration
        self.benchmark_cmd = benchmark_cmd
        self.mode = mode

        self.iter = 0
        self.target_pid = 0
        self.benchmark_pid = ""
        self.collector_list: List[PerfCollector] = []

        self._initialize()

    def _initialize(self):
        """初始化收集器"""
        # 获取目标进程PID
        if self.target_process_name:
            self.target_pid = int(self.get_process_pid())

        # 在ATTACH模式下启动基准测试
        if self.mode == COLLECTMODE.ATTACH_MODE:
            if not self.benchmark_cmd:
                raise ValueError("Benchmark command required in ATTACH mode")
            self.benchmark_pid = self.ssh_client.run_background_command(self.benchmark_cmd)

        # 初始化性能收集器
        self._initialize_collectors()

    def _initialize_collectors(self):
        """创建并配置性能收集器"""
        collectors = [
            TopDownCollector(),
            TlbCollector(),
            CacheCollector(),
            BranchCollector()
        ]

        for collector in collectors:
            collector.set_collector_param(
                self.ssh_client,
                self.duration,
                self.target_pid
            )
            self.collector_list.append(collector)

    def is_target_running(self) -> bool:
        """检查目标进程是否在运行"""
        # 检查主目标进程
        target_valid = (not self.target_pid or
                        self.is_pid_valid(self.target_pid))

        # 在ATTACH模式下检查基准测试进程
        benchmark_valid = (self.mode == COLLECTMODE.DIRECT_MODE or
                           (self.mode == COLLECTMODE.ATTACH_MODE and
                            self.is_pid_valid(self.benchmark_pid)))

        return target_valid and benchmark_valid

    def run(self) -> Dict[str, float]:
        """执行性能收集和分析"""
        if not self.is_target_running():
            raise RuntimeError("Target process not running")

        while self.iter < self.max_iteration:
            if not self.is_target_running():
                break

            for collector in self.collector_list:
                collector.collect()

            self.iter += 1

        # 处理收集到的数据
        all_data = {}
        for collector in self.collector_list:
            collector.process()
            all_data.update(collector.processed_data)

        return all_data

    def is_pid_valid(self, pid) -> bool:
        """检查PID是否有效"""
        cmd = f"ps -p {pid} > /dev/null 2>&1"
        result = self.ssh_client.run_cmd(cmd)
        return result.status_code == 0

    def get_process_pid(self) -> str:
        """获取进程PID"""
        cmd = f"pgrep -f {self.target_process_name}"
        result = self.ssh_client.run_cmd(cmd)
        if not result.output:
            raise RuntimeError(f"No process found: {self.target_process_name}")
        return sorted(result.output.split('\n'))[0]

    def print_processed_data(self):
        """打印处理后的性能数据"""
        for collector in self.collector_list:
            for metric, value in collector.processed_data.items():
                logging.info(f"{metric}: {value:.2f}")
