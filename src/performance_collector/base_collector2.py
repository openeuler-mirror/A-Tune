from abc import abstractmethod

class COLLECTMODE:
    DIRECT_MODE = 0
    ATTACH_MODE = 1

class HostInfo:
    def __init__(self, host_ip="", host_port=22, host_user="root", host_password=""):
        self.host_ip = host_ip
        self.host_port = host_port
        self.host_user = host_user
        self.host_password = host_password

# [NEW] shell_execute.py
import paramiko
from typing import Dict, Any, Tuple
import logging

def remote_execute(
    cmd: str,
    host_info: HostInfo
) -> Dict[str, Any]:
    # 创建SSH对象
    client = paramiko.SSHClient()
    # 允许连接不在known_hosts文件中的主机 
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # 连接到远程主机
        client.connect(host_info.host_ip, host_info.host_port, host_info.host_user, host_info.host_password, timeout=5)
        # 执行指令
        stdin, stdout, stderr = client.exec_command(cmd)
        # 获取执行结果
        result = stdout.read().decode()
        error = stderr.read().decode()
        status_code = stdout.channel.recv_exit_status()
        if status_code:
            raise RuntimeError(f"Error executing command '{cmd}': {error}")
        else:
            logging.info("Command '%s' executed successfully.", cmd)
            return {cmd: result}
    except Exception as e:
        raise RuntimeError(f"Exception occurred while executing command '{cmd}': {e}")
    finally:
        # 关闭连接
        client.close()

def remote_execute_with_exit_code(
    cmd: str,
    host_info: HostInfo
) -> Tuple[str, str, int]:
    # 创建SSH对象
    client = paramiko.SSHClient()
    # 允许连接不在known_hosts文件中的主机 
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # 连接到远程主机
        client.connect(host_info.host_ip, host_info.host_port, host_info.host_user, host_info.host_password, timeout=5)
        # 执行指令
        logging.debug(f"remote_execute_with_exit_code execute cmd {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        # 获取执行结果
        result = stdout.read().decode().strip()
        error = stderr.read().decode()
        status_code = stdout.channel.recv_exit_status()
        logging.debug(f"remote_execute_with_exit_code [{result}] [{error}] status_code {status_code}")
        return result, error, status_code
    except Exception as e:
        raise RuntimeError(f"Exception occurred while executing command '{cmd}': {e}")
    finally:
        # 关闭连接
        client.close()

def run_nohup_cmd(
    cmd: str,
    host_info: HostInfo
) -> str:
    cmd = f"nohup {cmd} > /dev/null 2>&1 & echo $!"

    pid, _, _ = remote_execute_with_exit_code(cmd, host_info)
    pid = pid.strip()
    logging.debug(f"luckky test pid is {pid}")
    if not pid.isdigit():
        raise RuntimeError("Failed to get PID")
    return pid

def get_process_pid(
    process_name: str,
    host_info: HostInfo
):
    cmd = f"pgrep -f {process_name}"
    pid, _, _ = remote_execute_with_exit_code(cmd, host_info)
    if not pid.isdigit():
        raise RuntimeError(f"Failed to get PID of process [{process_name}]")
    return pid



class BaseCollector:
    def __init__(self):
        # self.collect_mode = collect_mode
        self.raw_data = {}
        self.processed_data = {}
        self.collect_cmd = ""

    @abstractmethod
    def collect(self):
        pass
    
    @abstractmethod
    def process(self):
        pass


