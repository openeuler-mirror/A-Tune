"""
OceanBase 性能指标采集模块

作用：
  - 用于 A-Tune Euler Copilot 调优系统采集 OceanBase 应用层指标
"""

from typing import Dict
from src.utils.collector.metric_collector import snapshot_task, CollectMode
from src.utils.config.global_config import env_config
from src.utils.common import translate


# 从配置中读取 OceanBase 登录信息
ob_config = env_config.get("app_config").get("oceanbase", {})
ob_user = ob_config.get("user", "root@sysbench_tenant")
ob_password = ob_config.get("password", "")
ob_port = ob_config.get("port", 2881)
ob_host = ob_config.get("host", "127.0.0.1")
ob_database = ob_config.get("database", "oceanbase")

def _obclient_base(cmd: str) -> str:
    """
    拼接 obclient 执行命令模板
    """
    pwd_option = f"-p{ob_password}" if ob_password else ""
    return f"obclient -h{ob_host} -P{ob_port} -u{ob_user} {pwd_option} -D{ob_database} -A -e \"{cmd}\""


def _ob_parse(stdout: str) -> Dict:
    """
    通用 OceanBase 输出解析函数
    """
    result = {}
    lines = stdout.strip().split("\n")
    for line in lines:
        parts = line.split("\t")
        if len(parts) == 2:
            key, value = parts
            result[key.strip()] = value.strip()
    return result


# ----------------- 指标采集任务定义 -----------------

@snapshot_task(
    cmd=_obclient_base("show global status like 'connections';"),
    collect_mode=CollectMode.ASYNC,
    tag=translate("OceanBase 当前连接数", "Current number of OceanBase connections")
)
def parse_ob_connections(output: str) -> Dict:
    return {"connections": _ob_parse(output)}


@snapshot_task(
    cmd=_obclient_base("show global status like 'uptime';"),
    collect_mode=CollectMode.ASYNC,
    tag=translate("OceanBase 运行时间（秒）", "OceanBase Runtime (seconds)")
)
def parse_ob_uptime(output: str) -> Dict:
    return {"uptime": _ob_parse(output)}


@snapshot_task(
    cmd=_obclient_base("show global status like 'com_select';"),
    collect_mode=CollectMode.ASYNC,
    tag=translate("OceanBase SELECT 执行次数", "OceanBase SELECT Execution Count")
)
def parse_ob_com_select(output: str) -> Dict:
    return {"com_select": _ob_parse(output)}


@snapshot_task(
    cmd=_obclient_base("show global status like 'com_insert';"),
    collect_mode=CollectMode.ASYNC,
    tag=translate("OceanBase INSERT 执行次数", "OceanBase INSERT Execution Count")
)
def parse_ob_com_insert(output: str) -> Dict:
    return {"com_insert": _ob_parse(output)}


@snapshot_task(
    cmd=_obclient_base("show global status like 'com_update';"),
    collect_mode=CollectMode.ASYNC,
    tag=translate("OceanBase UPDATE 执行次数", "OceanBase SELUPDATEECT Execution Count")
)
def parse_ob_com_update(output: str) -> Dict:
    return {"com_update": _ob_parse(output)}


@snapshot_task(
    cmd=_obclient_base("show global status like 'com_delete';"),
    collect_mode=CollectMode.ASYNC,
    tag=translate("OceanBase DELETE 执行次数", "OceanBase DELETE Execution Count")
)
def parse_ob_com_delete(output: str) -> Dict:
    return {"com_delete": _ob_parse(output)}


@snapshot_task(
    cmd=_obclient_base("show global status like 'slow_queries';"),
    collect_mode=CollectMode.ASYNC,
    tag=translate("OceanBase 慢查询次数", "OceanBase Slow Query Count")
)
def parse_ob_slow_queries(output: str) -> Dict:
    return {"slow_queries": _ob_parse(output)}


@snapshot_task(
    cmd=_obclient_base("show processlist;"),
    collect_mode=CollectMode.ASYNC,
    tag=translate("OceanBase 当前进程列表", "OceanBase Current Process List")
)
def parse_ob_processlist(output: str) -> Dict:
    return {"processlist": output}


@snapshot_task(
    cmd=_obclient_base("show parameters;"),
    collect_mode=CollectMode.ASYNC,
    tag=translate("OceanBase 系统参数", "OceanBase System Parameters")
)
def parse_ob_parameters(output: str) -> Dict:
    """
    获取当前 OceanBase 参数列表（用于调优参考）
    """
    result = {}
    lines = output.strip().split("\n")
    for line in lines:
        parts = line.split("\t")
        if len(parts) >= 2:
            result[parts[0]] = parts[1]
    return {"parameters": result}
