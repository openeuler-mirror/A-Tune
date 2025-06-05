from .base_collector import BaseCollector
from typing import Dict, Any, List, Tuple
import logging
import json
from enum import Enum
from src.utils.llm import get_llm_response
from src.utils.shell_execute import remote_execute
from src.utils.json_repair import json_repair
import os
import yaml
from src.utils.shell_execute import SshClient


class MysqlMetric(Enum):
    TODO = "XX"


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# 查询是否开启慢查询日志
slow_log_query = "SHOW GLOBAL VARIABLES LIKE 'slow_query_log';"
# 慢查询次数
slow_query = "SHOW GLOBAL STATUS LIKE 'Slow_queries';"
# 查询是否开启profile
profile_query = "SHOW GLOBAL VARIABLES LIKE 'profiling';"
# 查询profile(文字呈现)
profile = "SHOW PROFILES"
# 查询processlist(文字呈现)
processlist_query = "SHOW PROCESSLIST"


def check_output(result):
    if result.status_code == 0:
        if isinstance(result.output, str):
            return result.output.isdigit()
    return False


def check_mysql_state(
    host_ip: str, host_port: str, host_user: str, host_password: str
) -> bool:
    check_mysql_state_cmd = "pgrep mysqld"

    ssh_client = SshClient(
        host_ip=host_ip,
        host_port=host_port,
        host_user=host_user,
        host_password=host_password,
    )
    mysql_state = ssh_client.run_cmd(check_mysql_state_cmd)

    return check_output(mysql_state)


def get_mysql_config() -> Tuple[str, str]:
    current_file_path = os.path.abspath(__file__)
    current_dir_path = os.path.dirname(current_file_path)
    app_config = os.path.join(current_dir_path, "..", "..", "config", "app_config.yaml")
    try:
        with open(app_config, "r") as f:
            app_config = yaml.safe_load(f)
        mysql_config = app_config["mysql"]
        return mysql_config["user"], mysql_config["password"]
    except Exception as e:
        logging.error(f"Failed to parse optimize_config.yaml: {e}")


def check_metric_stat(
    host_ip: str,
    host_port: str,
    host_user: str,
    host_password: str,
    mysql_user: str,
    mysql_password: str,
    cmd: str,
) -> bool:
    cmd = (
        f"mysql -s -N -e \"SHOW GLOBAL VARIABLES LIKE 'profiling';\""
        + f" -u{mysql_user} -p{mysql_password}"
    )
    res = remote_execute(
        cmd=cmd,
        host_ip=host_ip,
        host_port=host_port,
        host_user=host_user,
        host_password=host_password,
    )
    if "OFF" in res[cmd]:
        return False
    else:
        return True


def get_mysql_cmd(
    host_ip: str, host_port: str, host_user: str, host_password: str
) -> List[str]:
    is_mysql_running = check_mysql_state(
        host_ip=host_ip,
        host_port=host_port,
        host_user=host_user,
        host_password=host_password,
    )
    if not is_mysql_running:
        logging.info("mysql is not running")
        return []
    mysql_user, mysql_password = get_mysql_config()
    cmds = list(MYSQL_PARSE_FUNCTIONS.keys())
    is_slow_log_on_cmd = (
        f"mysql -s -N -e \"SHOW GLOBAL VARIABLES LIKE 'slow_query_log';\""
        + f" -u{mysql_user} -p{mysql_password}"
    )
    is_slow_log_on = check_metric_stat(
        host_ip=host_ip,
        host_port=host_port,
        host_user=host_user,
        host_password=host_password,
        mysql_user=mysql_user,
        mysql_password=mysql_password,
        cmd=is_slow_log_on_cmd,
    )
    if not is_slow_log_on:
        cmds.remove(f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Slow_queries';\"")
    is_profiling_on_cmd = (
        f"mysql -s -N -e \"SHOW GLOBAL VARIABLES LIKE 'profiling';\""
        + f" -u{mysql_user} -p{mysql_password}"
    )
    is_profiling_on = check_metric_stat(
        host_ip=host_ip,
        host_port=host_port,
        host_user=host_user,
        host_password=host_password,
        mysql_user=mysql_user,
        mysql_password=mysql_password,
        cmd=is_profiling_on_cmd,
    )
    if not is_profiling_on:
        cmds.remove(f'mysql -s -N -e "SHOW PROFILES"')
    for i in range(len(cmds)):
        cmds[i] = cmds[i] + f" -u{mysql_user} -p{mysql_password}"
    return cmds


def mysql_parse(stdout: Any) -> Dict:
    result = {}
    lines = stdout.strip().split("\n")
    for line in lines:
        parts = line.split("\t")  # 按制表符分割
        if len(parts) != 2:
            raise ValueError(f"格式错误：行 '{line}' 不包含两个部分")
        key, value = parts
        result[key.strip()] = value.strip()  # 去掉可能的多余空格
    return result


# profiling的输出是文字，不作多余解析
def profiling_parse(stdout: Any) -> Dict:
    return {"profiling": stdout}


# processlist的输出是文字，不作多余解析
def processlist_parse(stdout: Any) -> Dict:
    return {"processlist": stdout}


MYSQL_PARSE_FUNCTIONS = {
    # 查询MySQL服务器被连接次数
    f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Connections';\"": mysql_parse,
    # 查询MySQL服务上线（启动）时间（秒)
    f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Uptime';\"": mysql_parse,
    # 查询MySQL执行的SELECT返回行数及INSERT、UPDATE、DELETE操作的返回行数
    f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Innodb_rows_%';\"": mysql_parse,
    # 查询MySQL的增删改查的执行操作次数
    f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Com_select';\"": mysql_parse,
    f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Com_insert';\"": mysql_parse,
    f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Com_update';\"": mysql_parse,
    f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Com_delete';\"": mysql_parse,
    # 查询线程信息
    f"mysql -s -N -e \"SHOW STATUS LIKE '%THREAD%'\"": mysql_parse,
    # 慢查询次数
    f"mysql -s -N -e \"SHOW GLOBAL STATUS LIKE 'Slow_queries';\"": mysql_parse,
    # 查询profile
    f'mysql -s -N -e "SHOW PROFILES"': profiling_parse,
    # 查询processlist
    f'mysql -s -N -e "SHOW PROCESSLIST"': processlist_parse,
}


class MysqlCollector(BaseCollector):
    def __init__(self, cmd: List[str], **kwargs):
        kwargs["cmds"] = cmd
        super().__init__(**kwargs)

    def parse_cmd_stdout(
        self,
        mysql_info_stdout: Dict[str, Any],
    ) -> Dict:
        parse_result = {}
        for k, v in mysql_info_stdout.items():
            # 使用字典获取对应的解析函数，如果cmd不在字典中，使用默认的解析函数
            k = k[: k.find("-u")][:-1]
            parse_function = MYSQL_PARSE_FUNCTIONS.get(k, self.default_parse)
            cmd_parse_result = parse_function(v)
            parse_result = {**parse_result, **cmd_parse_result}
        return parse_result

    def data_process(
        self,
        mysql_parse_result: Dict,
    ) -> Dict:
        return mysql_parse_result
