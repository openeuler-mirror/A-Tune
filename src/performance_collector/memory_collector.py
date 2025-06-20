from .base_collector import BaseCollector
from typing import Dict, Any, List
import logging
from enum import Enum

class MemoryMetric(Enum):
    TODO = "XX"


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

omm_kill_cmd = "(oom_kill1=$(cat /proc/vmstat | grep oom_kill | awk '{print$2}'); sleep 5; oom_kill2=$(cat /proc/vmstat | grep oom_kill | awk '{print$2}')) && echo $((oom_kill2 - oom_kill1))"

def get_memory_cmd()-> List[str]:
    return list(MEMORY_PARSE_FUNCTIONS.keys())
def free_parse(
    cmd: str, 
    stdout: Any,
) -> Dict:
    if cmd != "free":
        logging.error("Command is not 'free'.")
        raise ValueError("Command is not 'free'.")

    if not isinstance(stdout, str):
        logging.error("Input stdout is not a string.")
        raise TypeError("Expected stdout to be a string")

    try:
        out = stdout.split("\n")
        out.pop()
        data = out[-1].split()
        total_swap = float(data[1])  
        free_swap = float(data[3])  

        res = {"总的交换空间总量": total_swap, "可用的交换空间总量": free_swap}
    except IndexError as e:
        logging.error(f"Failed to parse memory and swap usage: {e}")
        raise ValueError("Failed to parse memory and swap usage from stdout") from e
    except ValueError as e:
        logging.error(f"Failed to convert swap values to float: {e}")
        raise ValueError("Failed to convert swap values to float") from e

    return res

def omm_kill_parse(
    cmd: str,
    stdout: Any,
) -> Dict:
    if cmd != omm_kill_cmd:
        logging.error("Command is not 'omm_kill'.")
        raise ValueError("Command is not 'omm_kill'.")

    if not isinstance(stdout, str):
        logging.error("Input stdout is not a string.")
        raise TypeError("Expected stdout to be a string")

    try:
        omm_kill = float(stdout.split("\n")[0])
        res = {"omm_kill": omm_kill}
    except ValueError as e:
        logging.error(f"Failed to parse OOM killer count from stdout: {e}")
        raise ValueError("Failed to parse OOM killer count from stdout") from e

    return res

def sar_parse(
    cmd: str,
    stdout: Any,
) -> Dict:
    if cmd != "sar -r 1 1":
        logging.error("Command is not 'sar'.")
        raise ValueError("Command is not 'sar'.")

    if not isinstance(stdout, str):
        logging.error("Input stdout is not a string.")
        raise TypeError("Expected stdout to be a string")

    try:
        out = stdout.split("\n")
        out.pop()  
        date = out[-1].split()
        memory_usage = float(date[4]) 

        res = {"内存使用率": memory_usage}
    except IndexError as e:
        logging.error(f"Failed to parse memory usage from sar output: {e}")
        raise ValueError("Failed to parse memory usage from sar output") from e
    except ValueError as e:
        logging.error(f"Failed to convert memory usage to float: {e}")
        raise ValueError("Failed to convert memory usage to float") from e

    return res

MEMORY_PARSE_FUNCTIONS = {
    "free": free_parse,
    omm_kill_cmd: omm_kill_parse,
    "sar -r 1 1": sar_parse,
}

class MemoryCollector(BaseCollector):
    def __init__(self, cmd: List[str], **kwargs):
        kwargs['cmds'] = cmd
        super().__init__(**kwargs)

    def parse_cmd_stdout(
        self,
        memory_info_stdout: Dict[str, Any],
    ) -> Dict:
        parse_result = {}
        for k, v in memory_info_stdout.items():
            # 使用字典获取对应的解析函数，如果cmd不在字典中，使用默认的解析函数
            parse_function = MEMORY_PARSE_FUNCTIONS.get(k, self.default_parse)
            cmd_parse_result = parse_function(k, v)
            parse_result = {**parse_result, **cmd_parse_result}
        return parse_result

    def calculate_swap_usage(
        self,
        available_swap: float,
        total_swap: float
    ) -> float:
        """计算交换空间使用率"""
        if total_swap > 0:
            return 1 - (available_swap / total_swap)
        else:
            return 1

    def data_process(
        self,
        memory_parse_result: Dict,
    ) -> Dict:
        logging.info(f"[MemoryCollector] collecting memory workload metrics")
        memory_process_result = {}

        # 计算交换空间使用率
        memory_process_result["交换空间使用率"] = self.calculate_swap_usage(
            memory_parse_result["可用的交换空间总量"],
            memory_parse_result["总的交换空间总量"]
        )

        # 内存使用率
        memory_process_result["内存使用率"] = memory_parse_result["内存使用率"] / 100

        # # Swapout 判断
        # SWAPOUT_THRESHOLD = 5  # 定义阈值常量
        # memory_process_result["swapout"] = int(memory_parse_result["每秒从主内存交换到交换空间的页面数"] > SWAPOUT_THRESHOLD)

        # OOM Killer 判断
        memory_process_result["omm_kill"] = int(memory_parse_result["omm_kill"] > 0)

        return memory_process_result
