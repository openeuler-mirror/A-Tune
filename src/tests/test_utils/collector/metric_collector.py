import random
from src.tests.test_utils.collector import test_cpu_collector
from src.utils.thread_pool import thread_pool_manager, serial_task_manager
from src.utils.collector.metric_collector import (
    period_task,
    snapshot_task,
    CollectMode,
    CollectType,
    get_registered_module_tasks,
)


class Result:
    def __init__(self, status_code, output, cmd):
        self.status_code = status_code
        self.output = output
        self.cmd = cmd

    def __repr__(self):
        return self.output


class SshClient:
    def __init__(self):
        self.host_ip = "127.0.0.1"
        self.host_port = 22

    def run_cmd(self, cmd):
        return Result(0, str(random.uniform(0.6, 0.8)), cmd)


# 声明ssh client连接
ssh_client = SshClient()
# 获取test_cpu_collector通过修饰器注册的异步任务
async_tasks = get_registered_module_tasks(test_cpu_collector, CollectMode.ASYNC)
# 获取test_cpu_collector通过修饰器注册的同步任务
sync_tasks = get_registered_module_tasks(test_cpu_collector, CollectMode.SYNC)

# 异步任务入线程池
thread_pool_manager.add_batch(
    [(func_info["func"], (ssh_client,)) for func_info in async_tasks]
)

# 同步任务进入串行任务池
serial_task_manager.add_batch(
    [(func_info["func"], (ssh_client,)) for func_info in sync_tasks]
)


# 异步任务利用run_all_task()接口执行任务
thread_pool_manager.run_all_tasks()
# 异步任务利用get_all_results()接口阻塞程序，等待所有线程都ready
# 注意每次执行完一批任务后，下次执行会清空所有上一步的任务和结果，需要重新add任务
task_results = thread_pool_manager.get_all_results()

print("*" * 30 + "async results" + "*" * 30)
print(task_results)
print("*" * 30 + "async results" + "*" * 30)


# 同步任务同理
serial_task_manager.run_all_tasks()
task_results = serial_task_manager.get_all_results()
print("*" * 30 + "sync results" + "*" * 30)
print(task_results)
print("*" * 30 + "sync results" + "*" * 30)
