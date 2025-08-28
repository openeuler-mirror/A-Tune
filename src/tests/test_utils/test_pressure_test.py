# start_workflow.py
from src.performance_test.pressure_test import PressureTest, wait_for_pressure_test
import time


class SshClient:
    def __init__(self):
        self.host_ip = "127.0.0.1"
        self.host_port = 22

    def run_cmd(self, cmd):
        print(cmd)
        time.sleep(5)
        return 123.4

    def run_local_cmd(self, cmd):
        print(cmd)
        time.sleep(5)
        return 333.1


if __name__ == "__main__":
    # 初始化SSH客户端
    ssh_client = SshClient()

    # 创建压测线程
    app = "mysql"
    thread = PressureTest(app, ssh_client)
    thread.start()

    # 等待压测完成或超时
    result = wait_for_pressure_test(timeout=300)

    # 打印结果
    if isinstance(result, str):
        print(result)
    else:
        if result.status_code == 0:
            print("压测成功，结果如下：")
            print(result.output)
        else:
            print("压测失败，错误信息如下：")
            print(result.err_msg)
