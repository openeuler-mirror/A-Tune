import paramiko
import time
from typing import Dict, Any, Callable
import logging
from functools import wraps, partial
import inspect
from collections import defaultdict
from abc import abstractmethod
import traceback
from types import ModuleType
from src.utils.common import ExecuteResult

decorated_funcs = defaultdict(list)
cmds_registry = defaultdict(list)


# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def remote_execute(
    cmd: str = "",
    host_ip: str = "",
    host_port: int = 22,
    host_user: str = "root",
    host_password: str = "",
) -> Dict[str, Any]:
    # 创建SSH对象
    client = paramiko.SSHClient()
    # 允许连接不在known_hosts文件中的主机
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # 连接到远程主机
        client.connect(host_ip, host_port, host_user, host_password)
        # 执行指令
        stdin, stdout, stderr = client.exec_command(cmd)
        # 获取执行结果
        result = stdout.read().decode()
        error = stderr.read().decode()
        status_code = stdout.channel.recv_exit_status()
        if status_code:
            logging.error("Error executing command '%s': %s", cmd, error)
            return {cmd: result}
        else:
            logging.info("Command '%s' executed successfully.", cmd)
            return {cmd: result}
    except Exception as e:
        logging.error("Exception occurred while executing command '%s': %s", cmd, e)
        return None
    finally:
        client.close()


def retryable(max_retries: int = 3, delay: int = 1):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    retries += 1
                    print(
                        f"Attempt {retries} failed in function '{func.__name__}': {e}"
                    )
                    if retries < max_retries:
                        print(f"Retrying in {delay} second(s)...")
                        time.sleep(delay)
                    else:
                        print(
                            f"Function '{func.__name__}' failed after {retries} attempts."
                        )
                        raise

        return wrapper

    return decorator


class SshClient:
    def __init__(
        self,
        host_ip: str = "",
        host_port: int = 22,
        host_user: str = "root",
        host_password: str = "",
        max_retries: int = 0,
        delay: float = 1.0,
    ):
        self.host_ip = host_ip
        self.host_port = host_port
        self.host_user = host_user
        self.host_password = host_password

        self.max_retries = max_retries
        self.delay = delay

    @retryable()
    def run_cmd(self, cmd) -> ExecuteResult:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        result = ExecuteResult()
        try:
            client.connect(
                self.host_ip, self.host_port, self.host_user, self.host_password
            )
            _, stdout, stderr = client.exec_command(cmd)
            result.output = stdout.read().decode()
            result.err_msg = stderr.read().decode()
            result.status_code = stdout.channel.recv_exit_status()
        except Exception as e:
            result.status_code = -1
            result.output = ""
            result.err_msg = traceback.format_exc()
        finally:
            client.close()
        return result


def process_decorated_func(
    result: ExecuteResult, func: Callable, ssh_client: SshClient, *args, **kwargs
):
    try:
        processed_result = func(result.output, *args, **kwargs)
        result.output = processed_result
    except Exception as e:
        print(traceback.format_exc())
        result.err_msg = str(e)
    return result


def cmd_pipeline(
    cmd: str = "",
    tag: str = "default_tag",
    parallel: bool = False,
):
    def decorator(func):
        file = inspect.getfile(func)

        @wraps(func)
        def wrapper(ssh_client, *args, **kwargs):
            result = ssh_client.run_cmd(cmd)
            if result.status_code == 0:
                return process_decorated_func(result, func, ssh_client)
            return result

        decorated_funcs[file].append(
            {"func": wrapper, "tag": tag, "parallel": parallel}
        )
        return wrapper

    return decorator


def get_registered_cmd_funcs(
    ssh_client: SshClient, tag: str = "default_tag", parallel: bool = False
):
    stack = inspect.stack()
    if len(stack) < 2:
        return []
    frame = stack[1]
    caller_file = frame.filename

    registered_funcs = decorated_funcs.get(caller_file, [])

    func_list = []
    for func_info in registered_funcs:
        if func_info["parallel"]:
            func_list.append(
                (func_info["func"], (ssh_client,), {"tag": func_info["tag"]})
            )
    return func_list


def get_registered_cmd_funcs(
    module: ModuleType, tag: str = "default_tag", parallel: bool = True
):
    if not isinstance(module, ModuleType) or not hasattr(module, "__file__"):
        raise RuntimeError(
            f"module {module.__name__} has no attr __file__, maybe it is a built-in module"
        )
    caller_file = module.__file__

    registered_funcs = decorated_funcs.get(caller_file, [])

    func_list = []
    for func_info in registered_funcs:
        if func_info["parallel"] == parallel:
            func_list.append({"func": func_info["func"], "tag": func_info["tag"]})
    return func_list
