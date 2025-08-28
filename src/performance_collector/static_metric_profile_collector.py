import logging

from src.performance_collector import static_profile_collector
from src.utils.shell_execute import get_registered_cmd_funcs
from src.utils.thread_pool import ThreadPoolManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class StaticMetricProfileCollector:
    def __init__(
        self,
        ssh_client,
        max_workers
    ):
        self.ssh_client = ssh_client

        self.thread_pool = ThreadPoolManager(max_workers=max_workers)
        self.sequential_pool = []
        self._add_tasks(
            # 获取这些模块所有注册的cmd parser接口，提交到线程池执行
            static_profile_collector
        )

    def _add_tasks(self, *args):
        for module in args:
            func_info_list = get_registered_cmd_funcs(module)
            self.thread_pool.add_batch(
                [(func_info["func"], (self.ssh_client,), {"tag": func_info["tag"]}) for func_info in func_info_list]
            )

    def sequential_tasks(self):
        pass

    def run(self):
        logging.info(
            "[StaticMetricProfileCollector] collecting static profile data ..."
        )
        parsed_results = {}

        self.thread_pool.run_all_tasks()
        task_results = self.thread_pool.get_all_results()

        for task_result in task_results:
            if task_result.tag not in parsed_results:
                parsed_results[task_result.tag] = {}
            if task_result.result.status_code == 0:
                parsed_results[task_result.tag].update(task_result.result.output)
            else:
                logging.warning(f"error while execute task {task_result.func_name}, err_msg is {task_result.result}")

        return parsed_results
