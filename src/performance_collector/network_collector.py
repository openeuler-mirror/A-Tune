import logging
from enum import Enum
from typing import Dict, Any, List

from .base_collector import BaseCollector


class NetworkMetric(Enum):
    TODO = "XX"


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ListenOverflows = ("ListenOverflows1=$(cat /proc/net/netstat | grep 'TcpExt:' | awk '{print$20}' | tail -n 1); sleep 5;"
                   "ListenOverflows2=$(cat /proc/net/netstat | grep 'TcpExt:' | awk '{print$20}' | tail -n 1); "
                   "echo $((ListenOverflows2 - ListenOverflows1))")
FullDoCookies = ("FullDoCookies1=$(cat /proc/net/netstat | grep 'TcpExt:' | awk '{print$76}' | tail -n 1); sleep 5; "
                 "FullDoCookies2=$(cat /proc/net/netstat | grep 'TcpExt:' | awk '{print$76}' | tail -n 1); "
                 "echo $((FullDoCookies2 - FullDoCookies1))")
FullDrop = ("FullDrop1=$(cat /proc/net/netstat | grep 'TcpExt:' | awk '{print$77}' | tail -n 1); sleep 5; "
            "FullDrop2=$(cat /proc/net/netstat | grep 'TcpExt:' | awk '{print$20}' | tail -n 1); "
            "echo $(( FullDrop2 - FullDrop1))")


def get_network_cmd() -> List[str]:
    return list(NETWORK_PARSE_FUNCTIONS.keys())


def listenoverflows_parse(
        cmd: str,
        stdout: Any,
) -> Dict:
    if cmd != ListenOverflows:
        logging.error("Command is not 'ListenOverflows'.")
        raise ValueError("Command is not 'ListenOverflows'.")

    if not isinstance(stdout, str):
        logging.error("Input stdout is not a string.")
        raise TypeError("Expected stdout to be a string")

    try:
        listenOverflows = float(stdout.split("\n")[0])
        res = {"listenOverflows": listenOverflows}
    except ValueError as e:
        logging.error(f"Failed to parse listen overflows count from stdout: {e}")
        raise ValueError("Failed to parse listen overflows count from stdout") from e

    return res


def fulldocookies_parse(
        cmd: str,
        stdout: Any,
) -> Dict:
    if cmd != FullDoCookies:
        logging.error("Command is not 'FullDoCookies'.")
        raise ValueError("Command is not 'FullDoCookies'.")

    if not isinstance(stdout, str):
        logging.error("Input stdout is not a string.")
        raise TypeError("Expected stdout to be a string")

    try:
        fulldocookies = float(stdout.split("\n")[0])
        res = {"fulldocookies": fulldocookies}
    except (IndexError, ValueError) as e:
        logging.error(f"Failed to parse fulldocookies count from stdout: {e}")
        raise ValueError("Failed to parse fulldocookies count from stdout") from e

    return res


def fulldrop_parse(
        cmd: str,
        stdout: Any,
) -> Dict:
    if cmd != FullDrop:
        logging.error("Command is not 'FullDrop'.")
        raise ValueError("Command is not 'FullDrop'.")

    if not isinstance(stdout, str):
        logging.error("Input stdout is not a string.")
        raise TypeError("Expected stdout to be a string")

    try:
        fulldrop = float(stdout.split("\n")[0])
        res = {"fulldrop": fulldrop}
    except (IndexError, ValueError) as e:
        logging.error(f"Failed to parse fulldrop count from stdout: {e}")
        raise ValueError("Failed to parse fulldrop count from stdout") from e

    return res


def sar_parse(
        cmd: str,
        stdout: Any,
) -> Dict:
    if cmd != "sar -n DEV 1 1":
        logging.error("Command is not 'sar -n DEV 1 1'.")
        raise ValueError("Command is not 'sar -n DEV 1 1'.")
    return {"网卡指标": stdout}


NETWORK_PARSE_FUNCTIONS = {
    ListenOverflows: listenoverflows_parse,
    FullDoCookies: fulldocookies_parse,
    FullDrop: fulldrop_parse,
    "sar -n DEV 1 1": sar_parse,
}


class NetworkCollector(BaseCollector):
    def __init__(self, cmd: List[str], **kwargs):
        kwargs['cmds'] = cmd
        super().__init__(**kwargs)

    def parse_cmd_stdout(
            self,
            network_info_stdout: Dict[str, Any],
    ) -> Dict:
        parse_result = {}
        for k, v in network_info_stdout.items():
            # 使用字典获取对应的解析函数，如果cmd不在字典中，使用默认的解析函数
            parse_function = NETWORK_PARSE_FUNCTIONS.get(k, self.default_parse)
            cmd_parse_result = parse_function(k, v)
            parse_result = {**parse_result, **cmd_parse_result}
        return parse_result

    def data_process(
            self,
            network_parse_result: Dict,
    ) -> Dict:
        logging.info(f"[NetworkCollector] collecting network workload metrics")
        network_process_result = {"listenOverflows": int(network_parse_result["listenOverflows"] > 0),
                                  "fulldocookies": int(network_parse_result["fulldocookies"] > 0),
                                  "fulldrop": int(network_parse_result["fulldrop"] > 0),
                                  "网卡指标": network_parse_result["网卡指标"]}
        return network_process_result
