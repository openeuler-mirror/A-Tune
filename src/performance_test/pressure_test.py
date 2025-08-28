import time
import threading

from src.utils.shell_execute import SshClient
from src.utils.config.app_config import AppInterface
from src.utils.common import ExecuteResult

_pressure_test_running = threading.Event()  # 标志压测是否正在运行
_pressure_test_result = ExecuteResult(
    status_code=-1, output=None, err_msg="pressure test not start yet!"
)  # 注意除了PressureTest线程能修改外，其他线程不应修改该结果


def wait_for_pressure_test(timeout=3600):
    """
    等待压测线程完成或超时。
    :param timeout: 超时时间（秒，默认3600秒）
    :return: 压测结果或超时提示
    """
    start_time = time.time()
    while _pressure_test_running.is_set():
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            raise TimeoutError(f"[PressureTest] waiting for pressure test timeout.")
        time.sleep(1)
    return _pressure_test_result


class PressureTest(threading.Thread):
    def __init__(
        self,
        app: str,
        ssh_client: SshClient,
    ):
        super().__init__()
        self.app = app
        self.app_interface = AppInterface(ssh_client).get(app)
        self._result = None
        self.running = True
        self.daemon = True

    def get_result(self):
        return self._result

    def run(self):
        global _pressure_test_result
        global _pressure_test_running
        try:
            _pressure_test_running.set()
            benchmark_result = self.app_interface.benchmark()
            _pressure_test_result.status_code = 0
            _pressure_test_result.output = benchmark_result
        except Exception as e:
            _pressure_test_result.status_code = -1
            _pressure_test_result.err_msg = (
                f"pressure test failed, exception is {str(e)}"
            )
        finally:
            self.running = False
            _pressure_test_running.clear()
