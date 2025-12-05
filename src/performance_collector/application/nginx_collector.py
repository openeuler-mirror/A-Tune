import logging
import re

from src.config import config
from src.utils.common import translate
from src.utils.collector.metric_collector import (
    period_task,
    CollectMode,
)

NINGX_HOST = config["servers"][0]["listening_address"] if config["servers"][0]["listening_address"] else "127.0.0.1"
NINGX_PORT = config["servers"][0]["listening_port"] if config["servers"][0]["listening_port"] else 10000

NGINX_SAMPLE_INTERVAL = 5  # 每次采样间隔
SAMPLE_COUNT = 13  # 采样次数
DURATION = (SAMPLE_COUNT - 1) * NGINX_SAMPLE_INTERVAL  # 统计总时长（秒）


def parse_stub_status_text(text: str) -> dict:
    result = {}
    try:
        lines = text.strip().splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith("Active connections"):
                result["active_connections"] = int(line.split(":")[1].strip())
            elif line.startswith("server accepts handled requests"):
                continue
            elif re.match(r"^\d+\s+\d+\s+\d+", line):
                parts = list(map(int, line.split()))
                result["accepts"] = parts[0]
                result["handled"] = parts[1]
                result["requests"] = parts[2]
            elif line.startswith("Reading"):
                parts = re.findall(r"(\w+):\s*(\d+)", line)
                for key, value in parts:
                    result[key.lower()] = int(value)
    except Exception as e:
        result["error"] = f"Failed to parse stub_status: {str(e)}"
    return result


@period_task(
    cmd=f"curl -s http://{NINGX_HOST}:{NINGX_PORT}/status",
    tag=translate("nginx_status指标", "nginx_status metric"),
    delay=0,
    sample_count=SAMPLE_COUNT,
    interval=NGINX_SAMPLE_INTERVAL,
    collect_mode=CollectMode.ASYNC
)
def parse_nginx_status(output: list[str]) -> dict:
    parsed_list = [parse_stub_status_text(text) for text in output if text]
    if len(parsed_list) < 2:
        return {}

    # 统计连接状态均值
    conn_keys = ["active_connections", "reading", "writing", "waiting"]
    conn_sum = {k: 0 for k in conn_keys}
    valid_samples = 0

    for item in parsed_list:
        if all(k in item for k in conn_keys):
            valid_samples += 1
            for k in conn_keys:
                conn_sum[k] += item.get(k, 0)

    avg_conns = {
        f"{DURATION}s内平均{k}": conn_sum[k] // valid_samples if valid_samples > 0 else 0
        for k in conn_keys
    }

    # 统计累加指标的增量（以第1条和最后1条为基准）
    try:
        accepts_delta = parsed_list[-1]["accepts"] - parsed_list[0]["accepts"]
        handled_delta = parsed_list[-1]["handled"] - parsed_list[0]["handled"]
        requests_delta = parsed_list[-1]["requests"] - parsed_list[0]["requests"]
        avg_qps = requests_delta // DURATION
    except Exception:
        accepts_delta = handled_delta = requests_delta = avg_qps = 0

    result = {
        f"requests_growth_in_{DURATION}s": requests_delta,
        f"accepts_growth_in_{DURATION}s": accepts_delta,
        f"handled_growth_in_{DURATION}s": handled_delta,
        f"avg_qps_in_{DURATION}s": avg_qps,
    }
    result.update(avg_conns)
    return {"curl -s http://127.0.0.1:10000/status": result}
