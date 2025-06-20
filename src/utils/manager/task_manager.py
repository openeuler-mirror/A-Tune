import logging


from types import ModuleType
from tabulate import tabulate
from src.utils.shell_execute import SshClient
from src.utils.thread_pool import serial_task_manager, thread_pool_manager
from src.utils.collector.collector_trigger import TriggerEventListener, TriggerStatus
from src.utils.collector.metric_collector import (
    get_registered_module_tasks,
    get_registered_modules_tasks,
    CollectMode,
    CollectType,
)

MAX_TASK_TIMEOUT = 300
triggered_event_listener = TriggerEventListener()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def wait_for_signal():
    # waiting状态会阻塞程序，close状态和triggered状态是立即返回的
    event_status = triggered_event_listener.wait()

    if event_status == TriggerStatus.CLOSE:
        logging.info(f"[TaskManager] waiting for trigger signale timeout, skip tasks")
        return False
    return True


class AbstractTaskManager:

    def __init__(self, ssh_client: SshClient, timeout: int = 60):
        self.ssh_client = ssh_client
        self.timeout = timeout

    def _wrap_collector_task(self, tasks: list):
        return [
            (task["func"], (self.ssh_client,), {"tag": task.pop("tag", "default_tag")})
            for task in tasks
        ]

    def display_stats(self, collect_mode: CollectMode):
        if not self.modules:
            return

        logging.info(f"[{collect_mode.name} scheduler] collecting following metrics...")
        modules_name = {
            str(module.__name__).split(".")[-1]: module for module in self.modules
        }
        rows = []
        for module_name, module in modules_name.items():
            for collect_type in [CollectType.TRIGGERED, CollectType.DIRECT]:
                task_list = get_registered_module_tasks(
                    module, collect_mode, collect_type
                )
                for task in task_list:
                    rows.append(
                        [
                            module_name,
                            task["func"].__name__,
                            collect_type.name,
                            collect_mode.name,
                        ]
                    )

        if not rows:
            return
        table_str = tabulate(
            rows,
            headers=["module_name", "task_name", "collect_type", "collect_mode"],
            tablefmt="grid",
        )
        print("\n" + table_str + "\n")


# 给定注册任务的模块，获取对应任务
class SyncTasksManager(AbstractTaskManager):
    def __init__(
        self,
        ssh_client: SshClient,
        modules: list[ModuleType],
        timeout: int = 60,
    ):
        super().__init__(ssh_client=ssh_client, timeout=timeout)
        self.modules = modules
        self.direct_collect_tasks = get_registered_modules_tasks(
            modules=modules,
            collect_mode=CollectMode.SYNC,
            collect_type=CollectType.DIRECT,
        )
        self.triggered_collect_tasks = get_registered_modules_tasks(
            modules=modules,
            collect_mode=CollectMode.SYNC,
            collect_type=CollectType.TRIGGERED,
        )

    def run(self):
        self.display_stats(CollectMode.SYNC)
        direct_tasks = []
        triggered_tasks = []

        if len(self.direct_collect_tasks) > 0:
            # 优先执行直接采集的任务
            serial_task_manager.add_batch(
                self._wrap_collector_task(self.direct_collect_tasks)
            )

            serial_task_manager.run_all_tasks()
            direct_tasks = serial_task_manager.get_all_results()

        if len(self.triggered_collect_tasks) > 0 and wait_for_signal():
            serial_task_manager.add_batch(
                self._wrap_collector_task(self.triggered_collect_tasks)
            )

            serial_task_manager.run_all_tasks()

            triggered_tasks = serial_task_manager.get_all_results()

        return direct_tasks + triggered_tasks


class AsyncTaskManager(AbstractTaskManager):

    def __init__(
        self, ssh_client: SshClient, modules: list[ModuleType], timeout: int = 60
    ):
        super().__init__(ssh_client=ssh_client, timeout=timeout)
        self.modules = modules
        self.collect_tasks = get_registered_modules_tasks(
            modules=modules, collect_mode=CollectMode.ASYNC
        )

    def run(self):
        self.display_stats(CollectMode.ASYNC)
        thread_pool_manager.add_batch(self._wrap_collector_task(self.collect_tasks))

        thread_pool_manager.run_all_tasks()
        return thread_pool_manager.get_all_results()


class TaskManager:
    def __init__(
        self,
        ssh_client: SshClient,
        modules: list[ModuleType],
        timeout: int = 60,
        global_trigger_mode: bool = False,
        debug: bool = False,
    ):
        self.global_trigger_mode = global_trigger_mode
        self.debug = debug

        if global_trigger_mode:
            logging.info(f"using global trigger mode")

        self.sync_task_manager = SyncTasksManager(
            ssh_client=ssh_client, modules=modules, timeout=timeout
        )
        self.async_task_manager = AsyncTaskManager(
            ssh_client=ssh_client, modules=modules, timeout=timeout
        )

    def run(self):
        sync_result = self.sync_task_manager.run()
        async_result = self.async_task_manager.run()
        task_results = sync_result + async_result

        if self.debug:
            for task_result in task_results:
                if task_result.status_code != 0 or task_result.result.status_code:
                    print(task_result.result.output)

        collect_result = {}
        for task_result in task_results:
            if task_result.status_code == 0 and task_result.result.status_code == 0:
                collect_result[task_result.tag] = task_result.result.output.output
            else:
                logging.warning(f"failed to collect {task_result.tag}")
                print(task_result.result.err_msg)
        return collect_result
