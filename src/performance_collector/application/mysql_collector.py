from typing import Dict
from src.utils.common import translate

from src.utils.collector.metric_collector import (
    snapshot_task,
    CollectMode,
)
from src.utils.config.global_config import env_config

mysql_config = env_config.get("app_config").get("mysql")
mysql_user = mysql_config["user"]
mysql_password = mysql_config["password"]


@snapshot_task(
    cmd=f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Connections';\" -u{mysql_user} -p{mysql_password}",
    collect_mode=CollectMode.ASYNC,
    tag=translate("MySQL服务器连接次数", "MySQL Server Connection Count"),
)
def parse_mysql_connections(output: str) -> Dict:
    cmd = "mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Connections';\""
    result = _mysql_parse(output)
    return {cmd: result}


@snapshot_task(
    cmd=f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Uptime';\" -u{mysql_user} -p{mysql_password}",
    collect_mode=CollectMode.ASYNC,
    tag=translate("MySQL启动时间（秒）", "MySQL Startup Time (seconds)"),
)
def parse_mysql_uptime(output: str) -> Dict:
    cmd = "mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Uptime';\""
    result = _mysql_parse(output)
    return {cmd: result}


@snapshot_task(
    cmd=f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Innodb_rows_%';\" -u{mysql_user} -p{mysql_password}",
    collect_mode=CollectMode.ASYNC,
    tag=translate("MySQL Innodb 行操作数", "MySQL InnoDB Row Operations"),
)
def parse_mysql_innodb_rows(output: str) -> Dict:
    cmd = "mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Innodb_rows_%';\""
    result = _mysql_parse(output)
    return {cmd: result}


@snapshot_task(
    cmd=f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Com_select';\" -u{mysql_user} -p{mysql_password}",
    collect_mode=CollectMode.ASYNC,
    tag=translate("MySQL SELECT 执行次数", "MySQL SELECT Execution Count"),
)
def parse_mysql_com_select(output: str) -> Dict:
    cmd = "mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Com_select';\""
    result = _mysql_parse(output)
    return {cmd: result}


@snapshot_task(
    cmd=f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Com_insert';\" -u{mysql_user} -p{mysql_password}",
    collect_mode=CollectMode.ASYNC,
    tag=translate("MySQL INSERT 执行次数", "MySQL INSERT Execution Count"),
)
def parse_mysql_com_insert(output: str) -> Dict:
    cmd = "mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Com_insert';\""
    result = _mysql_parse(output)
    return {cmd: result}


@snapshot_task(
    cmd=f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Com_update';\" -u{mysql_user} -p{mysql_password}",
    collect_mode=CollectMode.ASYNC,
    tag=translate("MySQL UPDATE 执行次数", "MySQL UPDATE Execution Count"),
)
def parse_mysql_com_update(output: str) -> Dict:
    cmd = "mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Com_update';\""
    result = _mysql_parse(output)
    return {cmd: result}


@snapshot_task(
    cmd=f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Com_delete';\" -u{mysql_user} -p{mysql_password}",
    collect_mode=CollectMode.ASYNC,
    tag=translate("MySQL DELETE 执行次数", "MySQL DELETE Execution Count"),
)
def parse_mysql_com_delete(output: str) -> Dict:
    cmd = "mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Com_delete';\""
    result = _mysql_parse(output)
    return {cmd: result}


@snapshot_task(
    cmd=f"mysql -s -N -e \"SHOW STATUS LIKE '%THREAD%';\" -u{mysql_user} -p{mysql_password}",
    collect_mode=CollectMode.ASYNC,
    tag=translate("MySQL 线程信息", "MySQL Thread Information"),
)
def parse_mysql_threads(output: str) -> Dict:
    cmd = "mysql -s -N -e \"SHOW STATUS LIKE '%THREAD%'\""
    result = _mysql_parse(output)
    return {cmd: result}


@snapshot_task(
    cmd=f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Slow_queries';\" -u{mysql_user} -p{mysql_password}",
    collect_mode=CollectMode.ASYNC,
    tag=translate("MySQL 慢查询次数", "MySQL Slow Query Count"),
)
def parse_mysql_slow_queries(output: str) -> Dict:
    cmd = "mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Slow_queries';\""
    result = _mysql_parse(output)
    return {cmd: result}


@snapshot_task(
    cmd=f"mysql -s -N -e \"SHOW PROFILES;\" -u{mysql_user} -p{mysql_password}",
    collect_mode=CollectMode.ASYNC,
    tag=translate("MySQL Profiling 信息", "MySQL Profiling Information"),
)
def parse_mysql_profiles(output: str) -> Dict:
    cmd = "mysql -s -N -e \"SHOW PROFILES\""
    return {cmd: output}


@snapshot_task(
    cmd=f"mysql -s -N -e \"SHOW PROCESSLIST;\" -u{mysql_user} -p{mysql_password}",
    collect_mode=CollectMode.ASYNC,
    tag=translate("MySQL ProcessList 信息", "MySQL ProcessList Information"),
)
def parse_mysql_processlist(output: str) -> Dict:
    cmd = "mysql -s -N -e \"SHOW PROCESSLIST\""
    return {cmd: output}


def _mysql_parse(stdout: str) -> Dict:
    """
    通用MySQL输出解析：按制表符分割成键值对
    """
    result = {}
    lines = stdout.strip().split("\n")
    for line in lines:
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        key, value = parts
        result[key.strip()] = value.strip()
    return result
