import concurrent.futures
import uuid
import traceback
from typing import Any, Callable, Dict, Tuple, List, Union, Iterable

from src.utils.common import ExecuteResult


class TaskResult:
    def __init__(
        self,
        uuid: str,
        func_name: str = "",
        result: Any = None,
        status_code: int = 0,
        tag: str = "default_tag",
    ):
        self.uuid = uuid
        self.func_name = func_name
        self.result = result
        self.status_code = status_code
        self.tag = tag

    def __dict__(self):
        return {
            "uuid": self.uuid,
            "func_name": self.func_name,
            "result": self.result,
            "status_code": self.status_code,
            "tag": self.tag,
        }

    def __repr__(self):
        return str(self.__dict__())


"""
ThreadPoll Manager, used for accelerate speed of performance collector command
"""


class ThreadPoolManager:
    def __init__(self, max_workers: int = 5):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, concurrent.futures.Future] = {}
        self.all_results: List[Dict[str, Any]] = []
        self.pending: list[tuple[str, Callable, tuple, dict]] = []
        self.tag_map: dict = {}
        self.task_meta: Dict[str, str] = {}

    # add a task to be run, every task will be asigned a task id
    # user can query whether this task has been done by is_done method
    def add_task(self, func: Callable, *args, **kwargs) -> str:
        task_id = str(uuid.uuid4())
        self.pending.append((task_id, func, args, kwargs))
        self.task_meta[task_id] = func.__name__
        if "tag" in kwargs:
            self.tag_map[task_id] = kwargs["tag"]
        else:
            self.tag_map[task_id] = "default_tag"
        return task_id

    """
    batch submit tasks, for example:
    def hello():
        return "hello"

    def add(x, y):
        return x + y

    tasks = [
        hello,
        (add, (1, 2), {}),
        (add, (3, 4), {"z": 5})
    ]
    """

    def add_batch(
        self, tasks: Iterable[Union[Callable, Tuple[Callable, Tuple, Dict]]]
    ) -> List[str]:
        uuids = []
        for task in tasks:
            if callable(task):
                task_id = self.add_task(task, tag="default")
            elif isinstance(task, tuple):
                # (func, args, kwargs)
                func = task[0]
                args = task[1] if len(task) > 1 else ()
                kwargs = task[2] if len(task) > 2 else {}
                task_id = self.add_task(func, *args, **kwargs)
            else:
                raise ValueError(f"Unsupported task format: {task}")
            uuids.append(task_id)
        return uuids

    def add_multi_batch(self, *args) -> List[str]:
        uuids_all = []
        for task in args:
            if isinstance(task, list):
                uuids_batch = self.add_batch(task)
            else:
                raise ValueError(f"Unsupported task format: {task}")
            uuids_all.extend(uuids_batch)
        return uuids_all

    def run_all_task(self) -> None:
        for task_id, func, args, kwargs in self.pending:
            future = self.executor.submit(func, *args, **kwargs)
            self.tasks[task_id] = future
        self.pending.clear()

    # get task result by id
    def get_result(self, task_id: str) -> Any:
        future = self.tasks.get(task_id)
        if not future:
            raise ValueError(f"No such task: {task_id}")
        return future.result()

    # query whether task has been done
    def is_done(self, task_id: str) -> bool:
        future = self.tasks.get(task_id)
        if not future:
            raise ValueError(f"No such task: {task_id}")
        return future.done()

    # wait until all task done
    def wait_all(self) -> None:
        concurrent.futures.wait(self.tasks.values())
        self.all_results.clear()
        for task_id, future in self.tasks.items():
            func_name = self.task_meta.get(task_id, "unknown")
            try:
                result = future.result()
                status_code = 0
            except Exception as e:
                result = ExecuteResult(
                    status_code=-1, output="", err_msg=traceback.format_exc()
                )
                status_code = -1
            self.all_results.append(
                TaskResult(
                    task_id, func_name, result, status_code, self.tag_map[task_id]
                )
            )

    def get_all_results(self) -> List[Dict[str, Any]]:
        self.wait_all()
        return self.all_results
