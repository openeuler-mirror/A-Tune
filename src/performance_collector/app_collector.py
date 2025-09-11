import importlib
import logging

from src.utils.manager.task_manager import TaskManager
from src.utils.shell_execute import SshClient


def load_app_collector(app: str):
    # 构建模块路径和类名
    module_path = f"src.performance_collector.application.{app.lower()}_collector"
    try:
        # 动态导入模块（当前模块是包内的，使用相对导入）
        module = importlib.import_module(module_path, package=__package__)

        return module
    except (ImportError, AttributeError) as e:
        logging.error(
            f"no module named {module_path} can be found, will skip collect application workload data."
        )

    return None


class AppCollector:
    def __init__(
            self,
            ssh_client: SshClient,
            app: str = None,
    ):
        self.app = app
        app_collector_module = load_app_collector(self.app)

        if not app_collector_module:
            self.collector = None
        else:
            self.collector = TaskManager(
                ssh_client=ssh_client,
                modules=[app_collector_module],
                timeout=60,
            )

    def run(self):
        if not self.collector:
            return {}
        return self.collector.run()
