import logging
import inspect
import traceback

from time import sleep
from enum import Enum
from functools import wraps
from typing import Callable, Any
from types import ModuleType
from collections import defaultdict
from src.utils.common import ExecuteResult
from src.utils.collector.collector_trigger import TriggerStatus, TriggerEventListener

MAX_SAMPLE_COUNT = 100
MAX_SAMPLE_INTERVAL = 600
MAX_TASK_TIMEOUT = 300

trigger_event_listener = TriggerEventListener()


class CollectMode(Enum):
    SYNC = "sync"
    ASYNC = "async"


class CollectType(Enum):
    TRIGGERED = "triggered"
    DIRECT = "direct"


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

SYNC_DIRECT_TASKS = defaultdict(list)
ASYNC_TASKS = defaultdict(list)
SYNC_TRIGGERED_TASKS = defaultdict(list)

# 四种采集方式组合：同步+直接采集、同步+触发采集、异步+直接采集、异步+触发采集
# 对应四种任务队列，异步队列可以合并一起并行执行
# 触发式采集执行前会阻塞任务，若收到采集信号才会执行
TASK_MODE_MAP = {
    (CollectMode.SYNC, CollectType.DIRECT): SYNC_DIRECT_TASKS,
    (CollectMode.ASYNC, CollectType.DIRECT): ASYNC_TASKS,
    (CollectMode.SYNC, CollectType.TRIGGERED): SYNC_TRIGGERED_TASKS,
    (CollectMode.ASYNC, CollectType.TRIGGERED): ASYNC_TASKS,
}


def process_decorated_func(output: Any, func: Callable):
    result = ExecuteResult()
    try:
        result.output = func(output)
        result.err_msg = ""
        result.status_code = 0
    except Exception as e:
        print(traceback.format_exc())
        result.err_msg = str(e)
        result.output = ""
        result.status_code = -1
    return result


def period_task(
    cmd: str,
    tag: str = None,
    delay: int = 0,
    sample_count: int = 1,
    interval: int = 0,
    collect_mode: CollectMode = CollectMode.SYNC,
    collect_type: CollectType = CollectType.DIRECT,
):
    """
    周期采集任务
    cmd: 命令字符串
    tag: 任务标签
    delay: 延迟采集任务，等业务趋于平稳后采集，单位s
    sample_count: 周期任务采集次数
    interval: 周期任务采集时间间隔，单位s
    collect_mode: 采集任务的模式，有同步和异步两种
    collect_type: 采集类型，有直接采集（业务持续运行状态）和触发式采集（通过benchmark压测的状态）
    """

    def decorator(func):
        file = inspect.getfile(func)

        @wraps(func)
        def wrapper(ssh_client):
            result = ExecuteResult()
            if delay > 0:
                sleep(delay)

            if sample_count <= 0 or sample_count >= MAX_SAMPLE_COUNT:
                raise ValueError(
                    f"Invalid sample count {sample_count} for peroid task."
                )

            if interval <= 0 or interval >= MAX_SAMPLE_INTERVAL:
                raise ValueError(f"Invalid sample interval {interval} for peroid task.")

            if (
                collect_mode == CollectMode.ASYNC
                and collect_type == CollectType.TRIGGERED
            ):
                logging.info(
                    f"task {func.__name__} is a triggered event, waiting for fifo signal ..."
                )
                event_status = trigger_event_listener.wait()
                if event_status == TriggerStatus.CLOSE:
                    logging.info(
                        f"task {func.__name__} waiting for trigger signal timeout"
                    )
                    result.status_code = -1
                    result.err_msg = (
                        f"task {func.__name__} waiting for trigger signal timeout"
                    )
                    return result

            logging.info(
                f"period task {func.__name__} running, it will take {(sample_count - 1) * interval}s ..."
            )
            all_result = []

            for cnt in range(sample_count):
                cmd_result = ssh_client.run_cmd(cmd)
                if cmd_result.status_code == 0:
                    all_result.append(cmd_result.output)
                else:
                    all_result.append(None)
                    logging.warning(
                        f"failed to execute peroid task {func.__name__}, reason is {cmd_result.err_msg}"
                    )
                if cnt != sample_count - 1:
                    sleep(interval)

            if len(all_result) <= 0:
                result.status_code = -1
                result.err_msg = f"no data collected for peroid task {func.__name__}"
            else:
                processed_result = process_decorated_func(all_result, func)
                result.status_code = 0
                result.output = processed_result
                logging.info(f"task {func.__name__} finished!")

            return result

        TASK_MODE_MAP[(collect_mode, collect_type)][file].append(
            {"func": wrapper, "tag": tag}
        )
        return wrapper

    return decorator


def snapshot_task(
    cmd: str,
    tag: str = None,
    collect_mode: CollectMode = CollectMode.SYNC,
    collect_type: CollectType = CollectType.DIRECT,
):
    def decorator(func):
        file = inspect.getfile(func)

        @wraps(func)
        def wrapper(ssh_client):
            result = ExecuteResult()
            if (
                collect_mode == CollectMode.ASYNC
                and collect_type == CollectType.TRIGGERED
            ):
                logging.info(
                    f"task {func.__name__} is a triggered event, waiting for fifo signal ..."
                )
                event_status = trigger_event_listener.wait()
                if event_status == TriggerStatus.CLOSE:
                    logging.info(
                        f"task {func.__name__} waiting for trigger signal timeout"
                    )
                    result.status_code = -1
                    result.err_msg = (
                        f"task {func.__name__} waiting for trigger signal timeout"
                    )
                    return result

            logging.info(f"task {func.__name__} running ...")

            cmd_result = ssh_client.run_cmd(cmd)
            if cmd_result.status_code == 0:
                processed_result = process_decorated_func(cmd_result.output, func)
                result.status_code = cmd_result.status_code
                result.output = processed_result
                logging.info(f"task {func.__name__} finished!")
            else:
                result = cmd_result

            return result

        TASK_MODE_MAP[(collect_mode, collect_type)][file].append(
            {"func": wrapper, "tag": tag}
        )
        return wrapper

    return decorator


def get_registered_module_tasks(
    module: ModuleType,
    collect_mode: CollectMode = CollectMode.SYNC,
    collect_type: CollectType = CollectType.DIRECT,
):
    if not isinstance(module, ModuleType) or not hasattr(module, "__file__"):
        raise RuntimeError(
            f"module {module.__name__} has no attr __file__, maybe it is a built-in module"
        )
    caller_file = module.__file__
    return TASK_MODE_MAP[(collect_mode, collect_type)].get(caller_file, [])


def get_registered_modules_tasks(
    modules: list[ModuleType],
    collect_mode: CollectMode = CollectMode.SYNC,
    collect_type: CollectType = CollectType.DIRECT,
):
    task_list = []
    for module in modules:
        task_list.extend(
            get_registered_module_tasks(module, collect_mode, collect_type)
        )
    return task_list
