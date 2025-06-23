import logging
import importlib

from typing import Any
from src.performance_analyzer.application.mysql_analyzer import MysqlAnalyzer


def load_analyzer_class(app: str):
    try:
        # 构建模块路径和类名
        module_path = f".application.{app}_analyzer"
        class_name = f"{app.capitalize()}Analyzer"  # 可根据命名规则处理大小写

        # 动态导入模块（当前模块是包内的，使用相对导入）
        module = importlib.import_module(module_path, package=__package__)

        # 获取类对象
        collector_class = getattr(module, class_name)
        return collector_class
    except (ImportError, AttributeError) as e:
        logging.error(
            f"no module named {module_path}.{class_name} can be found, will skip analyze application workload."
        )

    return None


class AppAnalyzer:
    def __init__(self, app: str, data: Any):
        self.app_class = load_analyzer_class(app)
        if app.lower() == "mysql":
            self.app_analyzer = MysqlAnalyzer(data=data, app=app)
        else:
            if self.app_class:
                self.app_analyzer = self.app_class(data=data, app=app)
            else:
                self.app_analyzer = None

    def run(self):
        if not self.app_analyzer:
            return ""
        return self.app_analyzer.run()
