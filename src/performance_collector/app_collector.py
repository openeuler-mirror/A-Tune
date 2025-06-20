import importlib

from src.utils.shell_execute import SshClient
from src.utils.manager.task_manager import TaskManager
from src.performance_collector.application.mysql_collector import (
    MysqlCollector,
    get_mysql_cmd,
)


def load_app_collector(app: str):
    try:
        # 构建模块路径和类名
        module_path = f".application.{app.lower()}_collector"

        # 动态导入模块（当前模块是包内的，使用相对导入）
        module = importlib.import_module(module_path, package=__package__)

        return module
    except (ImportError, AttributeError) as e:
        raise ImportError(f"无法加载 {module_path}: {e}")


class AppCollector:
    def __init__(
        self,
        host_ip: str,
        host_port: int,
        host_user: str,
        host_password: str,
        ssh_client: SshClient,
        app: str = None
    ):
        self.app = app
        if self.app.lower() == "mysql":
            self.collector = MysqlCollector(
                cmd=get_mysql_cmd(
                    host_ip=host_ip,
                    host_port=host_port,
                    host_user=host_user,
                    host_password=host_password,
                ),
                host_ip=host_ip,
                host_port=host_port,
                host_user=host_user,
                host_password=host_password,
            )
        else:
            app_collector_module = load_app_collector(self.app)
            self.collector = TaskManager(
                ssh_client=ssh_client,
                modules=[app_collector_module],
                timeout=60,
            )

    def run(self):
        return self.collector.run()
