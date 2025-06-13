import logging

from typing import List
from types import ModuleType
from src.utils.shell_execute import get_registered_cmd_funcs, SshClient
from src.utils.thread_pool import ThreadPoolManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BaseMetricCollector:
    def __init__(
        self,
        ssh_client: SshClient,
        max_workers: int,
        registered_modules: List[ModuleType],
    ):
        self.ssh_client = ssh_client
        self.thread_pool = ThreadPoolManager(max_workers=max_workers)
        self._add_tasks(*registered_modules)

    def _add_tasks(self, *args):
        for module in args:
            if not isinstance(module, ModuleType):
                raise RuntimeError(
                    f"Arg must be `ModuleType` rather than `{type(module)}`"
                )

            func_info_list = get_registered_cmd_funcs(module)

            if not func_info_list:
                logging.warning(f"{module.__name__} is not a registered module!")

            self.thread_pool.add_batch(
                [
                    (func_info["func"], (self.ssh_client,), {"tag": func_info["tag"]})
                    for func_info in func_info_list
                ]
            )

    def run(self):
        logging.info("Collecting app profile data ...")
        parsed_results = {}

        self.thread_pool.run_all_task()

        task_results = self.thread_pool.get_all_results()

        for task_result in task_results:
            if task_result.tag not in parsed_results:
                parsed_results[task_result.tag] = {}
            
            if task_result.result.status_code == 0:
                parsed_results[task_result.tag].update(task_result.result.output)
            else:
                logging.error(
                    f"error while execute task {task_result.func_name}, err_msg is {task_result.result}"
                )

        return parsed_results
