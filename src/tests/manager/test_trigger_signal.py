import threading
from src.utils.collector.collector_trigger import TriggerEventListener


def wait_thread(name, listener):
    print(f"[{name}] 开始等待信号...")
    status = listener.wait()
    print(f"[{name}] 结束等待，状态为：{status.name}")


def main():
    listener = TriggerEventListener(timeout=2)  # 设置较长超时，等你手动写信号
    listener.run()

    import time
    time.sleep(3)
    # 启动两个等待线程
    threads = []
    for i in range(2):
        t = threading.Thread(target=wait_thread, args=(f"Worker-{i+1}", listener))
        t.start()
        threads.append(t)

    # 不自动触发信号，注释掉模拟线程
    # threading.Thread(target=simulate_fifo_signal, daemon=True).start()

    for t in threads:
        t.join()

    print("主线程最终状态：", listener.get_status().name)


if __name__ == "__main__":
    main()
