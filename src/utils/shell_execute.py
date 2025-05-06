import paramiko
from typing import Dict, Any
import logging
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
        # 关闭连接
        client.close()
