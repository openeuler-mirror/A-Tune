from typing import Dict, Any, List
import logging
import json
import re

from src.utils.shell_execute import cmd_pipeline, get_registered_cmd_funcs, SshClient
from src.utils.thread_pool import ThreadPoolManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@cmd_pipeline(cmd="cd /home/gitee/ && sh benchmark.sh")
def parse_mysql_sysbench(output: str) -> Dict:
    match = re.search(r"queries:\s+\d+\s+\(([\d.]+) per sec\.\)", output)

    if match:
        qps = match.group(1)
        return {"qps": qps}
    else:
        print(output)
        raise RuntimeError("Failed to execute mysql benchmark")

