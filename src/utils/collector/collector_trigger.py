import os
import select
import time
import threading
import logging
from enum import Enum, auto
from contextlib import contextmanager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# FIFO 文件路径
FIFO_PATH = "/tmp/euler-copilot-fifo"
MAX_WAIT_TIMEOUT = 300


class TriggerStatus(Enum):
    WAITING = auto()
    TRIGGERED = auto()
    CLOSE = auto()


class TriggerEventListener:
    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.fifo_path = FIFO_PATH
        self.timeout = MAX_WAIT_TIMEOUT
        self._status = TriggerStatus.WAITING
        self._status_lock = threading.Lock()
        self._condition = threading.Condition(self._status_lock)
        self._thread = None
        self._initialized = True

    def configure(self, timeout):
        if self._thread is not None:
            logging.warning("[TriggerEventListener] Already running, cannot configure.")
            return
        self.timeout = timeout
        return self

    def get_status(self) -> TriggerStatus:
        with self._status_lock:
            return self._status

    def wait(self, timeout=None) -> TriggerStatus:
        with self._condition:
            if self._thread is None or not self._thread.is_alive():
                return self._status
            if self._status in (TriggerStatus.TRIGGERED, TriggerStatus.CLOSE):
                return self._status
            if timeout is not None:
                end_time = time.time() + timeout
                while self._status == TriggerStatus.WAITING:
                    remaining = end_time - time.time()
                    if remaining <= 0:
                        break
                    self._condition.wait(timeout=remaining)
            else:
                while self._status == TriggerStatus.WAITING:
                    self._condition.wait()
            return self._status

    def _set_status(self, new_status: TriggerStatus):
        with self._condition:
            if self._status in (TriggerStatus.TRIGGERED, TriggerStatus.CLOSE):
                return

            self._status = new_status
            self._condition.notify_all()

    def run(self):
        if self._thread and self._thread.is_alive():
            logging.warning(
                "[TriggerEventListener] TriggerEventListener already running."
            )
            return

        def _listener():
            fifo_fd = None
            try:
                if os.path.exists(self.fifo_path):
                    os.remove(self.fifo_path)

                os.mkfifo(self.fifo_path, 0o666)

                fifo_fd = os.open(self.fifo_path, os.O_RDONLY | os.O_NONBLOCK)
                start_time = time.time()
                self._set_status(TriggerStatus.WAITING)

                while time.time() - start_time < self.timeout:
                    readable, _, _ = select.select([fifo_fd], [], [], 0.1)
                    if readable:
                        try:
                            data = os.read(fifo_fd, 1024)
                            if not data:
                                continue  # EOF，不阻塞，但忽略
                            signal = data.decode().strip()
                            if signal == "1":
                                self._set_status(TriggerStatus.TRIGGERED)
                                logging.info("[TriggerEventListener] received signal")
                                break
                            else:
                                logging.debug(
                                    f"[TriggerEventListener] ignore signal: {signal!r}"
                                )
                        except OSError as e:
                            logging.warning(f"[TriggerEventListener] read error: {e}")
                            continue
                else:
                    self._set_status(TriggerStatus.CLOSE)
                    logging.warning("[TriggerEventListener] timeout")
            finally:
                if fifo_fd is not None:
                    os.close(fifo_fd)
                if os.path.exists(self.fifo_path):
                    os.remove(self.fifo_path)

        self._set_status(TriggerStatus.WAITING)
        self._thread = threading.Thread(target=_listener, daemon=True)
        self._thread.start()
        logging.info(
            f"[TriggerEventListener] start listening at {self.fifo_path}, it will block euler-copilot until recieved signal from pressure test ..."
        )


@contextmanager
def fifo_signal_monitor(timeout=30):
    """
    监测 FIFO 文件信号的上下文管理器。
    如果在指定的超时时间内接收到信号，则返回 True，否则返回 False。
    ！！！注意，只能单线程环境使用
    """
    try:
        # 确保 FIFO 文件存在
        if not os.path.exists(FIFO_PATH):
            os.mkfifo(FIFO_PATH, 0o666)  # 设置权限为 666，允许所有用户读写

        # 打开 FIFO 文件以读取信号
        fifo_fd = os.open(FIFO_PATH, os.O_RDONLY | os.O_NONBLOCK)  # 使用非阻塞模式打开
        start_time = time.time()
        while time.time() - start_time < timeout:
            readable, _, _ = select.select([fifo_fd], [], [], 0.1)  # 每次检查 0.1 秒
            if readable:
                try:
                    # 读取一行数据
                    signal = (
                        os.read(fifo_fd, 1024).decode().strip()
                    )  # 最多读取 1024 字节
                    if signal == "1":
                        yield True
                        break
                    else:
                        yield False
                        break
                except OSError as e:
                    # 如果没有数据可读，忽略错误
                    continue
        else:
            # 超时
            yield False
    finally:
        # 关闭文件描述符
        os.close(fifo_fd)
        # 清理 FIFO 文件（可选）
        if os.path.exists(FIFO_PATH):
            os.remove(FIFO_PATH)


@contextmanager
def no_signal_monitor(timeout: int = 0):
    try:
        yield True
    finally:
        pass
