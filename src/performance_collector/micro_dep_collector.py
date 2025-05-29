# from .base_collector import BaseCollector, CollectorArgs
from .base_collector2 import BaseCollector, HostInfo, remote_execute_with_exit_code, run_nohup_cmd, get_process_pid
import logging
from typing import List
cfg_fw = {
    'dispatch_size': 4,
}
cfg_pmu_topdown = {
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
}

cfg_pmu_cache = {
    'r0001': 'l1i_refill',
    'r0014': 'l1i_access',
    'r0003': 'l1d_refill',
    'r0004': 'l1d_access',
    'r0028': 'l2i_refill',
    'r0027': 'l2i_access',
    'r0017': 'l2d_refill',
    'r0016': 'l2d_access',
    'r0008': 'inst_retired',
}

cfg_pmu_branch = {
    'r0011': 'cycle',
    'r200b': 'alu_isq_stall',
    'r200c': 'lsu_isq_stall',
    'r200d': 'fsu_isq_stall',
    'r0010': 'brmisspred',
    'r0012': 'brpred',
}

cfg_pmu_tlb = {
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
def is_number(s: str):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_pid_valid(
        pid: int,
        host_info: HostInfo
    ):
    check_cmd = f"ps -p {pid} > /dev/null 2>&1"
    _, _, exit_code = remote_execute_with_exit_code(check_cmd, host_info)
    return exit_code == 0
    # return os.path.exists(f'/proc/{pid}')


class COLLECTMODE:
    DIRECT_MODE = 0
    ATTACH_MODE = 1


prompt_dict = {
    "frontend_bound": "TopDown中的前端瓶颈（frontend bound）",
    "bad_spec": "TopDown中的预测失败瓶颈（bad speculation）",
    "retiring": "TopDown中的指令完成（retiring）",
    "backend_bound": "TopDown中的后端瓶颈（backend bound）",
    "frontend_latency_bound": "TopDown中的前端瓶颈下的前端延时瓶颈（frontend latency bound）",
    "frontend_bandwidth_bound": "TopDown中的前端瓶颈下的前端带宽瓶颈（frontend bandwidth bound）",
    "bs_mispred": "TopDown中的预测失败瓶颈中的分支预测失败瓶颈（bad speculation branch misprediction）",
    "bs_mclear": "TopDown中的预测失败瓶颈中的流水线清空瓶颈（bad speculation machine clears）",
    "core_bound": "TopDown中的后端瓶颈中的后端执行瓶颈（core bound）",
    "mem_bound": "TopDown中的后端瓶颈中的后端内存子系统瓶颈（memory bound）",
    "core_fsu_bound": "TopDown中的后端执行瓶颈中的浮点/向量计算瓶颈（core fsu bound）",
    "core_other_bound": "TopDown中的后端执行瓶颈中的后端其他执行瓶颈（core other bound）",
    "mem_l1_bound": "TopDown中的后端内存子系统瓶颈中的读取L1 cache造成的指令执行瓶颈（不包含L2/L3）",
    "mem_l2_bound": "TopDown中的后端内存子系统瓶颈中的读取L2 cache造成的指令执行瓶颈（不包含L1/L3）",
    "mem_l3_dram_bound": "TopDown中的后端内存子系统瓶颈中的读取L3以及内存造成的指令执行瓶颈（不包含L1/L2）",
    "mem_store_bound": "TopDown中的后端内存子系统瓶颈中的内存写瓶颈（memory store bound）",
    "context_switches": "上下文切换次数（context-switches）",
    "cpu_migrations": "进程在不同CPU核之间的迁移次数（cpu-migrations）",
    "page_faults": "缺页异常次数（page-faults）",
    "l1i_missrate": "L1指令miss rate",
    "l1d_missrate": "L1数据miss rate",
    "l2i_missrate": "L2指令miss rate",
    "l2d_missrate": "L2数据miss rate",
    "l1i_mpki": "L1指令每千条指令中miss次数",
    "l1d_mpki": "L1数据每千条指令中miss次数",
    "l2i_mpki": "L2指令每千条指令中miss次数",
    "l2d_mpki": "L2数据每千条指令中miss次数",
    "branch_missrate": "分支预测失败率（branch missrate）",
    "alu_isq_stall": "算术逻辑单元全部被占用导致的执行瓶颈",
    "lsu_isq_stall": "访存逻辑单元全部被占用导致的执行瓶颈",
    "fsu_isq_stall": "浮点单元全部被占用导致的执行瓶颈",
    "l1i_tlb_missrate": "L1指令快表miss rate（l1i_tlb_missrate）",
    "l1d_tlb_missrate": "L1数据快表miss rate（l1d_tlb_missrate）",
    "l2i_tlb_missrate": "L2指令快表miss rate（l2i_tlb_missrate）",
    "l2d_tlb_missrate": "L2数据快表miss rate（l2d_tlb_missrate）",
    "itlb_walk_rate": "指令页表缓存未命中时触发页表遍历的频率（itlb_walk_rate）",
    "dtlb_walk_rate": "数据页表缓存未命中时触发页表遍历的频率（dtlb_walk_rate）",
    "l1i_tlb_mpki": "L1指令TLB每千条指令中miss次数",
    "l1d_tlb_mpki": "L1数据TLB每千条指令中miss次数",
    "l2i_tlb_mpki": "L2指令TLB每千条指令中miss次数",
    "l2d_tlb_mpki": "L2数据TLB每千条指令中miss次数",
    "itlb_walk_mpki": "指令TLB每千条指令中到页表查找次数",
    "dtlb_walk_mpki": "指令TLB每千条指令中到页表查找次数",
    "div_stall": "除法指令在关键路径导致的执行瓶颈",
}


class PerfCollector(BaseCollector):
    def __init__(self, cfg_pmu={}):
        self.cfg_pmu: dict = cfg_pmu
        super().__init__()

    def set_collector_param(self, host_info: HostInfo, duration=0.1, target_pid=0):
        self.host_info = host_info
        self.duration = duration
        self.target_pid = target_pid
        self._gen_collect_cmd()

    def _gen_collect_cmd(self):
        cmd = f"perf stat -e {','.join(self.cfg_pmu.keys())} "
        if self.target_pid:
            cmd += f"-p {self.target_pid} sleep {self.duration}"
        else:
            cmd += f"-a sleep {self.duration}"

        logging.debug(f"cmd: {cmd}")
        self.collect_cmd = cmd


    def collect(self):
        raw_data = {}
        _, stderr, _ = remote_execute_with_exit_code(
            cmd=self.collect_cmd,
            host_info=self.host_info,
        )
        for line in stderr.splitlines():
            line = line.rstrip()
            logging.debug(f"raw output: {line}")
            if line == "":
                continue
            elems = line.split()
            if len(elems) < 2:
                continue
            value = elems[0].replace(',', '')
            if value == "<not":
                logging.error(f"error this event is not counted: {line}")
                raw_data[elems[2]] = 0
            if is_number(value):
                raw_data[elems[1]] = value
        logging.debug(f"raw_data is {raw_data}")

        for k, v in raw_data.items():
            if k in self.cfg_pmu.keys():
                if self.cfg_pmu[k] in self.raw_data.keys():
                    self.raw_data[self.cfg_pmu[k]] += float(v)
                else:
                    self.raw_data[self.cfg_pmu[k]] = float(v)


class TopDownCollector(PerfCollector):
    def __init__(self, cfg_pmu={}, cfg_fw={}):
        self.cfg_fw = cfg_fw
        super().__init__(cfg_pmu)

    def process(self):
        # L1
        self.processed_data['frontend_bound'] = self.raw_data['fetch_bubble'] / (self.cfg_fw["dispatch_size"] * self.raw_data['cycle']) * 100
        self.processed_data['bad_spec'] = (self.raw_data['inst_spec'] - self.raw_data['inst_retired']) / (self.cfg_fw["dispatch_size"] * self.raw_data['cycle']) * 100
        self.processed_data['retiring'] = self.raw_data['inst_retired'] / (self.cfg_fw["dispatch_size"] * self.raw_data['cycle']) * 100
        self.processed_data['backend_bound'] = 100 - self.processed_data['frontend_bound'] - self.processed_data['bad_spec'] - self.processed_data['retiring']

        # L2
        self.processed_data['frontend_latency_bound'] = self.raw_data['fetch_bubble_max'] / self.raw_data['cycle'] * 100
        self.processed_data['frontend_bandwidth_bound'] = self.processed_data['frontend_bound'] - self.processed_data['frontend_latency_bound']
        self.processed_data['bs_mispred'] = self.processed_data['bad_spec'] * self.raw_data['brmisspred'] / (self.raw_data['brmisspred'] + self.raw_data['o3flush'])
        self.processed_data['bs_mclear'] = self.processed_data['bad_spec'] - self.processed_data['bad_spec'] * self.raw_data['brmisspred'] / (self.raw_data['brmisspred'] + self.raw_data['o3flush'])
        self.processed_data['core_bound'] = (self.raw_data['execstall_cycle'] - self.raw_data['memstall_anystore'] - self.raw_data['memstall_anyload']) / self.raw_data['execstall_cycle'] * self.processed_data['backend_bound']
        self.processed_data['mem_bound'] = (self.raw_data['memstall_anyload'] + self.raw_data['memstall_anystore']) / self.raw_data['execstall_cycle'] * self.processed_data['backend_bound']
        
        # L3
        self.processed_data['core_fsu_bound'] = self.raw_data['fsustall'] / self.raw_data['cycle'] * 100
        self.processed_data['core_other_bound'] = self.processed_data['core_bound'] - self.processed_data['core_fsu_bound']
        self.processed_data['mem_l1_bound'] = (self.raw_data['memstall_anyload'] - self.raw_data['memstall_l1miss']) / self.raw_data['execstall_cycle'] * self.processed_data['backend_bound']
        self.processed_data['mem_l2_bound'] = (self.raw_data['memstall_anyload'] - self.raw_data['memstall_l2miss']) / self.raw_data['execstall_cycle'] * self.processed_data['backend_bound']
        self.processed_data['mem_l3_dram_bound'] = self.raw_data['memstall_l2miss'] / self.raw_data['execstall_cycle'] * self.processed_data['backend_bound']
        self.processed_data['mem_store_bound'] = self.raw_data['memstall_anystore'] / self.raw_data['execstall_cycle'] * self.processed_data['backend_bound']

        # other
        # self.processed_data['cpu_freq'] = self.raw_data['cycle'] / self.raw_data['cpu_clock'] / 1e6 # MHz
        self.processed_data['context_switches'] = self.raw_data['context_switches']
        self.processed_data['cpu_migrations'] = self.raw_data['cpu_migrations']
        self.processed_data['page_faults'] = self.raw_data['page_faults']


class CacheCollector(PerfCollector):
    def __init__(self, cfg_pmu={}):
        super().__init__(cfg_pmu)

    def process(self):
        self.processed_data['l1i_missrate'] = self.raw_data['l1i_refill'] / self.raw_data['l1i_access'] * 100
        self.processed_data['l1d_missrate'] = self.raw_data['l1d_refill'] / self.raw_data['l1d_access'] * 100

        self.processed_data['l2i_missrate'] = self.raw_data['l2i_refill'] / self.raw_data['l2i_access'] * 100
        self.processed_data['l2d_missrate'] = self.raw_data['l2d_refill'] / self.raw_data['l2d_access'] * 100

        self.processed_data['l1i_mpki'] = self.raw_data['l1i_refill'] / self.raw_data['inst_retired'] * 1000
        self.processed_data['l1d_mpki'] = self.raw_data['l1d_refill'] / self.raw_data['inst_retired'] * 1000

        self.processed_data['l2i_mpki'] = self.raw_data['l2i_refill'] / self.raw_data['inst_retired'] * 1000
        self.processed_data['l2d_mpki'] = self.raw_data['l2d_refill'] / self.raw_data['inst_retired'] * 1000

class BranchCollector(PerfCollector):
    def __init__(self, cfg_pmu={}):
        super().__init__(cfg_pmu)

    def process(self):
        self.processed_data['branch_missrate'] = self.raw_data['brmisspred'] / (self.raw_data['brmisspred'] + self.raw_data['brpred']) * 100

        self.processed_data['alu_isq_stall'] = self.raw_data['alu_isq_stall'] / self.raw_data['cycle'] * 100
        self.processed_data['lsu_isq_stall'] = self.raw_data['lsu_isq_stall'] / self.raw_data['cycle'] * 100
        self.processed_data['fsu_isq_stall'] = self.raw_data['fsu_isq_stall'] / self.raw_data['cycle'] * 100


class TlbCollector(PerfCollector):
    def __init__(self, cfg_pmu={}):
        super().__init__(cfg_pmu)

    def process(self):
        self.processed_data['l1i_tlb_missrate'] = self.raw_data['l1i_tlb_refill'] / self.raw_data['l1i_tlb'] * 100
        self.processed_data['l1d_tlb_missrate'] = self.raw_data['l1d_tlb_refill'] / self.raw_data['l1d_tlb'] * 100

        self.processed_data['l2i_tlb_missrate'] = self.raw_data['l2i_tlb_refill'] / self.raw_data['l2i_tlb'] * 100
        self.processed_data['l2d_tlb_missrate'] = self.raw_data['l2d_tlb_refill'] / self.raw_data['l2d_tlb'] * 100

        self.processed_data['itlb_walk_rate'] = self.raw_data['itlb_walk'] / self.raw_data['l1i_tlb'] * 100
        self.processed_data['dtlb_walk_rate'] = self.raw_data['dtlb_walk'] / self.raw_data['l1d_tlb'] * 100

        self.processed_data['l1i_tlb_mpki'] = self.raw_data['l1i_tlb_refill'] / self.raw_data['inst_retired'] * 1000
        self.processed_data['l1d_tlb_mpki'] = self.raw_data['l1d_tlb_refill'] / self.raw_data['inst_retired'] * 1000

        self.processed_data['l2i_tlb_mpki'] = self.raw_data['l2i_tlb_refill'] / self.raw_data['inst_retired'] * 1000
        self.processed_data['l2d_tlb_mpki'] = self.raw_data['l2d_tlb_refill'] / self.raw_data['inst_retired'] * 1000

        self.processed_data['itlb_walk_mpki'] = self.raw_data['itlb_walk'] / self.raw_data['inst_retired'] * 1000
        self.processed_data['dtlb_walk_mpki'] = self.raw_data['dtlb_walk'] / self.raw_data['inst_retired'] * 1000

        self.processed_data['div_stall'] = self.raw_data['divstall'] / self.raw_data['cycle'] * 100


class MicroDepCollector:
    def __init__(self, host_info: HostInfo, target_process_name="", iteration=1000, duration=0.1, benchmark_cmd="", mode=COLLECTMODE.DIRECT_MODE):

        self.collector_list: List[PerfCollector] = []
        self.host_info = host_info
        self.target_process_name = target_process_name
        self.max_iteration = iteration
        self.iter = 0
        self.duration = duration
        self.mode = mode

        self.target_pid = get_process_pid(target_process_name, host_info)

        if self.mode == COLLECTMODE.ATTACH_MODE and not benchmark_cmd:
            logging.error(f'benchmark cmd is required in attach mode')

        if self.mode == COLLECTMODE.ATTACH_MODE:
            self.benchmark_pid = run_nohup_cmd(
                benchmark_cmd, 
                host_info
            )
        topdown_collector = TopDownCollector(cfg_pmu=cfg_pmu_topdown, cfg_fw=cfg_fw)
        tlb_collector = TlbCollector(cfg_pmu=cfg_pmu_tlb)
        cache_collector = CacheCollector(cfg_pmu=cfg_pmu_cache)
        branch_collector = BranchCollector(cfg_pmu=cfg_pmu_branch)
        self.add_collector(topdown_collector)
        self.add_collector(tlb_collector)
        self.add_collector(cache_collector)
        self.add_collector(branch_collector)


    def add_collector(self, collector: PerfCollector):
        if not isinstance(collector, PerfCollector):
            logging.error(f'collector is not a property type!')
        collector.set_collector_param(self.host_info, self.duration, self.target_pid)
        self.collector_list.append(collector)

    def is_target_running(self):
        # logging.info(f"{not self.target_pid} {is_pid_valid(self.target_pid)} {self.mode == COLLECTMODE.ATTACH_MODE} {self.benchmark_proc.poll() is not None}")
        return (
            (not self.target_pid or is_pid_valid(self.target_pid, self.host_info)) and
            (self.mode == COLLECTMODE.DIRECT_MODE or (self.mode == COLLECTMODE.ATTACH_MODE and is_pid_valid(self.benchmark_pid, self.host_info)))
        )

    def run(self):
        if not self.is_target_running():
            raise ValueError("Target process is not existed, please check the target pid!")
        while self.iter < self.max_iteration:
            for collector in self.collector_list:
                if self.is_target_running():
                    collector.collect()
                else:
                    # target process is end, stop collection
                    self.iter = self.max_iteration
                    break
            self.iter += 1


        for collector in self.collector_list:
            collector.process()
        all_data_dict = {}
        for collector in self.collector_list:
            all_data_dict.update(collector.processed_data)
        return all_data_dict
        
    def print_processed_data(self):
        for collector in self.collector_list:
            for item in collector.processed_data.items():
                logging.info(item)
