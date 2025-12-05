from .base_collector import BaseCollector
from typing import Dict, Any, List
from src.utils.common import translate
import logging
import json
from enum import Enum

class CpuMetric(Enum):
    ONE_MINUTE_AVG_LOAD = "1min"
    FIVE_MINUTE_AVG_LOAD  = "5min"
    TEN_MINUTE_AVG_LOAD  = "10min"

perf = "perf stat -e 'syscalls:*' -a sleep 1 2>&1 | grep syscalls| awk '{sum += $1} END {print sum}'"

def get_cpu_cmd()-> List[str]:
    return list(CPU_PARSE_FUNCTIONS.keys())

def nproc_parse(
    cmd: str,
    stdout: Any,
) -> Dict:
    if cmd != "nproc":
        logging.error("Command is not 'nproc'.")
        raise ValueError("Command must be 'nproc'")
    
    if not isinstance(stdout, str):
        logging.error("Input stdout is not a string.")
        raise TypeError("Expected stdout to be a string")

    try:
        logical_cpu_cores = int(stdout.split("\n")[0])
    except (IndexError, ValueError) as e:
        logging.error(f"Failed to parse CPU count from stdout: {e}")
        raise ValueError("Failed to parse CPU count from stdout") from e

    res = {"cpu_core_count": logical_cpu_cores}
    return res

def loadavg_parse(
    cmd: str,
    stdout: Any,
) -> Dict:
    if cmd != "cat /proc/loadavg":
        logging.error("Command is not 'cat /proc/loadavg'.")
        raise ValueError("Command must be 'cat /proc/loadavg'")
    
    if not isinstance(stdout, str):
        logging.error("Input stdout is not a string.")
        raise TypeError("Expected stdout to be a string")

    try:
        out = stdout.split("\n")
        data = out[0].split()
        if len(data) < 3:
            raise ValueError("Not enough data to parse load averages.")
        
        load_avgs = {"past_1min_average_load": float(data[0]),
                     "past_5min_average_load": float(data[1]),
                     "past_10min_average_load": float(data[2])}
    except (IndexError, ValueError) as e:
        logging.error(f"Failed to parse system load averages from stdout: {e}")
        raise ValueError("Failed to parse system load averages from stdout") from e

    return load_avgs

def perf_syscall_parse(
    cmd: str,
    stdout: Any,
) -> Dict:
    if cmd != perf:
        logging.error("Command is not 'perf'.")
        raise ValueError("Command must be 'perf'")

    if not isinstance(stdout, str):
        logging.error("Input stdout is not a string.")
        raise TypeError("Expected stdout to be a string")

    try:
        sys_call_rate = float(stdout.split("\n")[0])
    except (IndexError, ValueError) as e:
        logging.error(f"Failed to parse system call rate from stdout: {e}")
        raise ValueError("Failed to parse system call rate from stdout") from e

    res = {"system_calls_per_unit_time": sys_call_rate}
    return res

def mpstat_parse(
    cmd: str,
    stdout: Any,
) -> Dict:
    if cmd != "mpstat -P ALL -o JSON 1 1":
        logging.error("Command is not 'mpstat'.")
        raise ValueError("Command must be 'mpstat'")

    if not isinstance(stdout, str):
        logging.error("Input stdout is not a string.")
        raise TypeError("Expected stdout to be a string")

    try:
        stdout_data = json.loads(stdout)
        data = stdout_data["sysstat"]["hosts"][0]["statistics"][0]["cpu-load"][0]

        usr, nice, sys, iowait, irq, soft, steal, guest, gnice, idle = map(float, (data["usr"], data["nice"], data["sys"], data["iowait"], data["irq"], data["soft"], data["steal"], data["guest"], data["gnice"], data["idle"]))   
        res = {
            "user_mode_utilization": usr,
            "nice_priority_utilization": nice,
            "kernel_mode_utilization": sys,
            "io_wait_percentage": iowait,
            "hardware_interrupt_percentage": irq,
            "software_interrupt_percentage": soft,
            "virtual_machine_steal_time_percentage": steal,
            "guest_operating_system_utilization": guest,
            "nice_guest_utilization": gnice,
            "idle_time_percentage": idle
        }
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON from stdout: {e}")
        raise ValueError("Failed to parse JSON from stdout") from e
    except (IndexError, ValueError, TypeError) as e:
        logging.error(f"Failed to parse mpstat CPU statistics: {e}")
        raise ValueError("Failed to parse mpstat CPU statistics") from e

    return res

def process_parse(cmd, stdout):
    if cmd != "ps aux|wc -l":
        logging.error("Command is not 'ps aux|wc -l'.")
        raise ValueError("Command is not 'ps aux|wc -l'.")

    if not isinstance(stdout, str):
        logging.error("Input stdout is not a string.")
        raise TypeError("Expected stdout to be a string")

    try:
        total_process = float(stdout.split("\n")[0])
    except (ValueError, IndexError) as e:
        logging.error(f"Failed to parse total process count from stdout: {e}")
        raise ValueError("Failed to parse total process count from stdout") from e

    res = {"total_process_count": total_process}
    return res

def vmstat_parse(
    cmd: str,
    stdout: Any,
) -> Dict:
    if cmd != "vmstat 1 2":
        logging.error("Command is not 'vmstat'.")
        raise ValueError("Command is not 'vmstat'.")

    if not isinstance(stdout, str):
        logging.error("Input stdout is not a string.")
        raise TypeError("Expected stdout to be a string")

    try:
        out = stdout.split("\n")
        out.pop() 
        data = out[-1].split()

        runtime_num = int(data[0])  
        blocked_num = int(data[1])  
        context_switch = int(data[11])  

        res = {
            "running_process_count": runtime_num,
            "blocked_process_count": blocked_num,
            "context_switch_per_second": context_switch
        }
    except IndexError as e:
        logging.error(f"Failed to parse vmstat memory attributes: {e}")
        raise ValueError("Failed to parse vmstat memory attributes from stdout") from e
    except ValueError as e:
        logging.error(f"Failed to convert vmstat values to expected types: {e}")
        raise ValueError("Failed to convert vmstat values to expected types") from e

    return res

def pid_parse(
    cmd: str,
    stdout: Any,
) -> Dict:
    if cmd != "pidstat -d | head -6":
        logging.error("Command is not 'pidstat'.")
        raise ValueError("Command is not 'pidstat'.")
    return {"process_information": stdout}

CPU_PARSE_FUNCTIONS = {
    "nproc": nproc_parse,
    "cat /proc/loadavg": loadavg_parse,
    perf: perf_syscall_parse,
    "mpstat -P ALL -o JSON 1 1": mpstat_parse,
    "ps aux|wc -l": process_parse,
    "vmstat 1 2": vmstat_parse,
    "pidstat -d | head -6": pid_parse,
}

class CpuCollector(BaseCollector):
    def __init__(self, cmd: List[str], **kwargs):
        # 将cmd添加到kwargs中
        kwargs['cmds'] = cmd
        super().__init__(**kwargs)

    def parse_cmd_stdout(
        self,
        cpu_info_stdout: Dict[str, Any],
    ) -> Dict:
        parse_result = {}
        for k, v in cpu_info_stdout.items():
            # 使用字典获取对应的解析函数，如果cmd不在字典中，使用默认的解析函数
            parse_function = CPU_PARSE_FUNCTIONS.get(k, self.default_parse)
            cmd_parse_result = parse_function(k, v)
            parse_result = {**parse_result, **cmd_parse_result}
        return parse_result

    def normalize_percentage(
        self,
        value: Any, 
        total: float,
    ) -> float:
        return value / total if total != 0 else 0

    def is_heavy_load(
        self,
        usage: float,
    ) -> bool:
        return usage > 70

    def data_process(
        self, 
        cpu_parse_result: Dict,
    ) -> Dict:
        logging.info(f"[CpuCollector] collecting cpu workload metrics")
        cpu_process_result = {}

        # 计算平均负载
        for metric in [CpuMetric.ONE_MINUTE_AVG_LOAD, CpuMetric.FIVE_MINUTE_AVG_LOAD, CpuMetric.TEN_MINUTE_AVG_LOAD]:
            cpu_process_result[metric.value] = self.normalize_percentage(
                # cpu_parse_result[f"过去{metric.value}平均负载"], 
                cpu_parse_result[f"past_{metric.value}_average_load"],
                cpu_parse_result["cpu_core_count"]
            )

        # 计算CPU利用率
        cpu_utilizations = [
            "user_mode_utilization",
            "nice_priority_utilization",
            "kernel_mode_utilization"
        ]
        for utilization in cpu_utilizations:
            cpu_process_result[utilization] = self.normalize_percentage(
                cpu_parse_result[utilization], 100
            )

        # 其他百分比计算
        for key in [
            "hardware_interrupt_percentage",
            "software_interrupt_percentage",
            "virtual_machine_steal_time_percentage",
            "guest_operating_system_utilization",
            "nice_guest_utilization"
        ]:
            cpu_process_result[key] = self.normalize_percentage(
                cpu_parse_result[key], 100
            )

        # 计算CPU利用率和上下文切换次数
        cpu_process_result["cpu_utilization"] = 1 - self.normalize_percentage(
            cpu_parse_result["idle_time_percentage"], 100
        )
        cpu_process_result["context_switch_per_second"] = cpu_parse_result.get(
            "context_switch_per_second", 0
        )

        # 阻塞进程率
        cpu_process_result["blocked_process_rate"] = self.normalize_percentage(
            cpu_parse_result["blocked_process_count"], cpu_parse_result["total_process_count"]
        )

        # 确保内核态执行时的CPU利用率不为0
        cpu_process_result["kernel_mode_utilization"] = max(
            0.01, cpu_process_result["kernel_mode_utilization"]
        )

        # 判断计算密集型或IO密集型
        user_mode_ratio = cpu_process_result["user_mode_utilization"] / cpu_process_result["kernel_mode_utilization"]
        is_heavy_io = self.is_heavy_load(cpu_process_result["user_mode_utilization"]) or self.is_heavy_load(cpu_process_result["kernel_mode_utilization"])

        if user_mode_ratio > 2:
            cpu_process_result["compute_intensive"] = 1 if is_heavy_io else 0
        else:
            cpu_process_result["compute_intensive"] = 0

        if user_mode_ratio < 2:
            cpu_process_result["io_intensive"] = 1 if is_heavy_io else 0
        else:
            cpu_process_result["io_intensive"] = 0

        # 复制其他信息
        cpu_process_result["process_information"] = cpu_parse_result.get("process_information", [])
        cpu_process_result["system_calls_per_unit_time"] = cpu_parse_result.get("system_calls_per_unit_time", 0)
        cpu_process_result["cpu_core_count"] = cpu_parse_result.get("cpu_core_count", 0)

        return cpu_process_result
