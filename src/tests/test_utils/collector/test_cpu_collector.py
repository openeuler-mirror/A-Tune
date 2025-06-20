from src.utils.collector.metric_collector import (
    period_task,
    snapshot_task,
    CollectMode,
    CollectType,
)


@period_task(
    cmd="top",
    delay=2,
    sample_count=10,
    interval=1,
    collect_mode=CollectMode.ASYNC,
    collect_type=CollectType.DIRECT,
)
def cpu_usage_parser(output_list: list[str]):
    total_cpu_usage = 0.0
    for output in output_list:
        if not output:
            continue
        total_cpu_usage += float(output)
    return {"avg_cpu_usage": total_cpu_usage / len(output_list)}


@snapshot_task(
    cmd="aaa", collect_mode=CollectMode.ASYNC, collect_type=CollectType.TRIGGERED
)
def numa_parser(output: str):
    return {"numa_number": output}


@snapshot_task(
    cmd="test", collect_mode=CollectMode.SYNC, collect_type=CollectType.DIRECT
)
def memory_usage_parser(output: str):
    import time

    time.sleep(5)
    return {"memory_usage": output}


@snapshot_task(
    cmd="test", collect_mode=CollectMode.SYNC, collect_type=CollectType.DIRECT
)
def disk_usage_parser(output: str):
    import time

    time.sleep(2)
    return {"disk_usage": output}
