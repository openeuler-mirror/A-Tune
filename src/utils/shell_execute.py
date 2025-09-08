import inspect
import logging
import shlex
import subprocess
import time
import traceback
from collections import defaultdict
from functools import wraps
from types import ModuleType
from typing import Callable

import paramiko

from src.utils.common import ExecuteResult

decorated_funcs = defaultdict(list)
cmds_registry = defaultdict(list)

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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
            result.output = stdout.read().decode().strip()
            result.err_msg = stderr.read().decode()
            result.status_code = stdout.channel.recv_exit_status()
        except Exception as e:
            result.status_code = -1
            result.output = ""
            result.err_msg = traceback.format_exc()
        finally:
            client.close()
        return result

    @retryable()
    def run_local_cmd(self, cmd):
        result = ExecuteResult()
        try:
            # 使用 shlex.split 将命令字符串分割为参数列表
            args = shlex.split(cmd)
            shell_result = subprocess.run(
                args,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            result.output = shell_result.stdout.strip()
            result.err_msg = shell_result.stderr.strip()
            result.status_code = shell_result.returncode
        except subprocess.CalledProcessError as e:
            result.output = ""
            result.err_msg = e.stderr.strip()
            result.status_code = e.returncode
        except Exception as e:
            result.output = ""
            result.err_msg = str(e)
            result.status_code = -1
        return result

    @retryable()
    def run_background_command(self, cmd) -> str:
        """在后台运行命令并返回PID"""
        full_cmd = f"nohup {cmd} > /dev/null 2>&1 & echo $!"
        result = self.run_cmd(full_cmd)
        pid = result.output
        pid = pid.strip()
        if not pid.isdigit():
            raise RuntimeError("Failed to get PID")
        return pid


def process_decorated_func(
        result: ExecuteResult, func: Callable, *args, **kwargs
):
    try:
        processed_result = func(result.output, *args, **kwargs)
        result.output = processed_result
    except Exception as e:
        print(traceback.format_exc())
        result.status_code = -1
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
                return process_decorated_func(result, func)
            return result

        decorated_funcs[file].append(
            {"func": wrapper, "tag": tag, "parallel": parallel}
        )
        return wrapper

    return decorator


def get_registered_cmd_funcs(
        module: ModuleType, parallel: bool = True
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
