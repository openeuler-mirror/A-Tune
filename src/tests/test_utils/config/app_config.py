from src.utils.config.app_config import AppInterface
from src.tests.mock_ssh_client import SshClient

ssh_client = SshClient()
app_interface = AppInterface(ssh_client)
mysql = app_interface.mysql
sys = app_interface.system

res = mysql.get_param("hello")
print(res.cmd)
res = mysql.set_param("hello", 1)
print(res.cmd)
res = mysql.start_workload()
print(res.cmd)
res = mysql.stop_workload()
print(res.cmd)
res = mysql.benchmark()
print(res.cmd)

res = sys.get_param("aaa")
print(res.cmd)
res = sys.set_param("bbb", 2)
print(res.cmd)
