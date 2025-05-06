from .base_collector import BaseCollector
from typing import Dict, Any, List
import logging
import json
from enum import Enum

class DiskMetric(Enum):
    TODO = "XX"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_disk_cmd()-> List[str]:
    return list(DISK_PARSE_FUNCTIONS.keys())

def parse_disk_data(
    data: Dict[str, Any],
) -> Dict:
    device_name = data["disk_device"]
    r, rkb, w, wkb = float(data["r/s"]), float(data["rkB/s"]), float(data["w/s"]), float(data["wkB/s"])
    return {device_name: {"单位时间读速率": r, "单位时间读大小": rkb, "单位时间写速率": w, "单位时间写大小": wkb}}

def parse_disk_util_data(
    a_data: Any,
    b_data: Any,
) -> Dict:
    device_name = b_data["disk_device"]
    wait = (float(b_data["r_await"]) + float(b_data["w_await"]) + float(b_data["d_await"])
            - float(a_data["r_await"]) - float(a_data["w_await"]) - float(a_data["d_await"]))
    aqu_sz = float(b_data["aqu-sz"]) - float(a_data["aqu-sz"])
    util = float(b_data["util"])
    return {device_name: {"磁盘平均等待时间变化趋势": wait, "磁盘平均请求队列长度变化趋势": aqu_sz, "磁盘利用率": util}}

def iostat_parse(cmd, stdout):
    if cmd == "iostat -o JSON -dx 1 2":
        try:
            stdout = json.loads(stdout)
            disk = [parse_disk_data(data) for data in stdout["sysstat"]["hosts"][0]["statistics"][1]["disk"]]
            res = {"磁盘读写性能": disk}
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON from stdout: {e}")
            raise ValueError("Failed to parse JSON from stdout") from e
    elif cmd == "iostat -o JSON -dx 1 2; sleep 5; iostat -o JSON -dx 1 2":
        try:
            split_index = stdout.index('}\n{"sysstat": {')
            a, b = stdout[:split_index+2], stdout[split_index+2:]
            a = a[:-1]
            a_json = json.loads(a)
            b_json = json.loads(b)
            disk = [parse_disk_util_data(a_data, b_data) for a_data, b_data in zip(
                a_json["sysstat"]["hosts"][0]["statistics"][1]["disk"],
                b_json["sysstat"]["hosts"][0]["statistics"][1]["disk"])]
            res = {"磁盘利用": disk}
        except (ValueError, json.JSONDecodeError) as e:
            logging.error(f"Failed to parse disk utilization data: {e}")
            raise ValueError("Failed to parse disk utilization data") from e
    else:
        logging.warning("Received unknown command.")
        return {"error": "Unknown command"}

    return res

DISK_PARSE_FUNCTIONS = {
    "iostat -o JSON -dx 1 2": iostat_parse,
    "iostat -o JSON -dx 1 2; sleep 5; iostat -o JSON -dx 1 2": iostat_parse,
}

class DiskCollector(BaseCollector):
    def __init__(self, cmd: List[str], **kwargs):
        kwargs['cmds'] = cmd
        super().__init__(**kwargs)
    
    def parse_cmd_stdout(
        self,
        disk_info_stdout: Dict[str, Any],
    ) -> Dict:
        parse_result = {}
        for k, v in disk_info_stdout.items():
            # 使用字典获取对应的解析函数，如果cmd不在字典中，使用默认的解析函数
            parse_function = DISK_PARSE_FUNCTIONS.get(k, self.default_parse)
            cmd_parse_result = parse_function(k, v)
            parse_result = {**parse_result, **cmd_parse_result}
        return parse_result

    def data_process(
        self,
        disk_parse_result: Dict,
    ) -> Dict:
        disk_process_result = {
            # "iowait": disk_parse_result["系统有未完成的磁盘I/O请求时，等待IO占用CPU的百分比"] / 100,
            "磁盘信息": disk_parse_result["磁盘利用"],
        }
        for i in range(len(disk_process_result["磁盘信息"])):
            for key in disk_process_result["磁盘信息"][i]:
                disk_process_result["磁盘信息"][i][key].update(disk_parse_result["磁盘读写性能"][i][key])
        
        return disk_process_result




    
