import logging
from typing import Dict

from src.performance_collector import static_profile_collector
from src.utils.shell_execute import get_registered_cmd_funcs
from src.utils.thread_pool import ThreadPoolManager

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
            func_info_list = get_registered_cmd_funcs(module, parallel = True)
            task_batch = []
            for func_info in func_info_list:
                func = func_info["func"]
                func_args = (self.ssh_client,)
                func_kwargs = {"tag": func_info["tag"]}
                task_batch.append((func, func_args, func_kwargs))
            self.thread_pool.add_batch(task_batch)

    def sequential_tasks(self):
        pass

    def run(self):
        logging.info("[StaticMetricProfileCollector] collecting static profile data ...")
        parsed_results: Dict[str, Dict] = {}

        self.thread_pool.run_all_tasks()
        task_results = self.thread_pool.get_all_results()

        for task_result in task_results:
            if task_result.status_code != 0:
                logging.warning(f"failed to execute task {task_result.func_name}, exception is {task_result.result}")
                continue
            if task_result.tag not in parsed_results:
                parsed_results[task_result.tag] = {}
            # each task returns ExecueteResult object, and its output is dict of matric key and values
            if task_result.result.status_code == 0:
                parsed_results[task_result.tag].update(task_result.result.output)
            else:
                logging.warning(f"error while execute task {task_result.func_name}, err_msg is {task_result.result.err_msg}")

        return parsed_results
