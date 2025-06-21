from src.utils.collector.collector_trigger import fifo_signal_monitor, no_signal_monitor, TriggerEventListener


trigger_event_listener = TriggerEventListener()
def test_fifo_signal_monitor():
    print("开始测试...")
    with fifo_signal_monitor(timeout=5) as signal_received:
        if signal_received:
            print("在超时时间内接收到信号，继续执行...")
        else:
            print("超时未接收到信号，终止执行。")


def test_no_fifo_signal_monitor():
    print("开始测试...")
    with no_signal_monitor(timeout=30) as signal_received:
        if signal_received:
            print("在超时时间内接收到信号，继续执行...")
        else:
            print("超时未接收到信号，终止执行。")


# test_fifo_signal_monitor()
# test_no_fifo_signal_monitor()

trigger_event_listener.run()

trigger_event_listener.wait()

print("triggered signal")
