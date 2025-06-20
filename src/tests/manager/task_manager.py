import logging
import pyfiglet
from tabulate import tabulate

from src.tests.mock_ssh_client import SshClient
from src.utils.manager.task_manager import TaskManager
from src.utils.shell_execute import SshClient
from src.config import config
from src.performance_collector.application import pgsql_collector
from src.performance_analyzer.application.pgsql_analyzer import PgsqlAnalyzer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

host_ip = config["servers"][0]["ip"]
host_port = config["servers"][0]["port"]
host_user = config["servers"][0]["host_user"]
host_password = config["servers"][0]["password"]
app = config["servers"][0]["app"]
max_retries = config["servers"][0]["max_retries"]
delay = config["servers"][0]["delay"]
target_process_name = config["servers"][0]["target_process_name"]
benchmark_cmd = config["benchmark_cmd"]
need_restart_application = config["feature"][0]["need_restart_application"]
need_microDep_collector = config["feature"][0]["microDep_collector"]

ssh_client = SshClient(
    host_ip=host_ip,
    host_port=host_port,
    host_user=host_user,
    host_password=host_password,
    max_retries=max_retries,
    delay=delay,
)

task_manager = TaskManager(
    ssh_client=ssh_client,
    modules=[pgsql_collector],
    global_trigger_mode=False,
    timeout=60,
    debug=True
)

result = task_manager.run()

print(result)
