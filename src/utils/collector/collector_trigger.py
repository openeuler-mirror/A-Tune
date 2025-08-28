import logging
import threading
import time
from enum import Enum, auto

import paramiko

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


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TriggerEventListener:
    """
    单例：在后台线程里通过 SSH 轮询远程文件内容，
    当内容为 '1' 时把状态置为 TRIGGERED。
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *a, **kw):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_ready", False):
            return
        self._ready = True

        # 远程信息（可在 configure 中修改）
        self.host = None
        self.port = 22
        self.user = None
        self.password = None
        self.remote_path = FIFO_PATH

        self.timeout = 300
        self.poll_interval = 1.0  # 秒

        self._status = TriggerStatus.WAITING
        self._status_lock = threading.Lock()
        self._cond = threading.Condition(self._status_lock)
        self._thread = None
        self._stop_evt = threading.Event()

    # ---------- 配置 ----------
    def configure(self, host, port, user, password):
        if self._thread and self._thread.is_alive():
            logging.warning("RemoteSSHTrigger already running, ignore configure.")
            return self
        self.host, self.port = host, port
        self.user, self.password = user, password
        self.remote_path = FIFO_PATH
        self.timeout = 300
        self.poll_interval = 1.0
        return self

    # ---------- 状态 ----------
    def get_status(self) -> TriggerStatus:
        with self._status_lock:
            return self._status

    def wait(self, timeout=None):
        with self._cond:
            if self._status in (TriggerStatus.TRIGGERED, TriggerStatus.CLOSE):
                return self._status
            if timeout is None:
                while self._status == TriggerStatus.WAITING:
                    self._cond.wait()
            else:
                end = time.time() + timeout
                while self._status == TriggerStatus.WAITING:
                    left = end - time.time()
                    if left <= 0:
                        break
                    self._cond.wait(timeout=left)
            return self._status

    def _set_status(self, new_status: TriggerStatus):
        with self._cond:
            if self._status in (TriggerStatus.TRIGGERED, TriggerStatus.CLOSE):
                return
            self._status = new_status
            self._cond.notify_all()

    # ---------- 启动 ----------
    def run(self):
        if self._thread and self._thread.is_alive():
            logging.warning("already running")
            return
        self._stop_evt.clear()
        self._set_status(TriggerStatus.WAITING)
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        logging.info("RemoteSSHTrigger started polling %s@%s:%s",
                     self.user, self.host, self.remote_path)

    def stop(self):
        self._stop_evt.set()
        if self._thread:
            self._thread.join(timeout=5)

    # ---------- 后台线程 ----------
    def _worker(self):
        start = time.time()
        ssh = None
        try:
            ssh = self._connect()
            while not self._stop_evt.is_set():
                if time.time() - start >= self.timeout:
                    self._set_status(TriggerStatus.CLOSE)
                    break
                try:
                    val = self._read_remote(ssh).strip()
                    if val == "1":
                        self._delete_remote(ssh)
                        self._set_status(TriggerStatus.TRIGGERED)
                        break
                except Exception as e:
                    logging.warning("read error: %s", e)
                    # 可重连
                    ssh = self._reconnect(ssh)

                time.sleep(self.poll_interval)
        finally:
            if ssh:
                ssh.close()

    def _connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = None
        ssh.connect(self.host, port=self.port,
                    username=self.user,
                    password=self.password,
                    pkey=pkey,
                    timeout=10)
        return ssh

    def _reconnect(self, old_ssh):
        try:
            old_ssh.close()
        except:
            pass
        return self._connect()

    def _read_remote(self, ssh):
        cmd = f"cat {self.remote_path}"
        _, stdout, _ = ssh.exec_command(cmd, timeout=5)
        return stdout.read().decode()

    def _delete_remote(self, ssh):
        """删除 remote_path，失败仅警告"""
        cmd = f"rm -f {self.remote_path}"
        try:
            _, stdout, stderr = ssh.exec_command(cmd, timeout=5)
            exit_code = stdout.channel.recv_exit_status()
            if exit_code == 0:
                logging.debug("已删除远程文件 %s", self.remote_path)
            else:
                logging.debug("删除远程文件失败，exit=%s, err=%s",
                                exit_code, stderr.read().decode())
        except Exception as e:
            logging.debug("删除远程文件异常: %s", e)


if __name__ == "__main__":
    # 1. 配置
    listener = TriggerEventListener().configure(
        host="9.82.36.53",
        user="root",
        password="Huawei12#$",
        port="22"

    )

    # 2. 启动
    listener.run()

    # 3. 等待触发
    status = listener.wait()
    print("trigger status:", status)

    # 4. 后续逻辑
    print("继续在本机执行其他命令...")
