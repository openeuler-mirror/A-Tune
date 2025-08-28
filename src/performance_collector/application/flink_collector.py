import json
import logging

from src.config import config
from src.utils.collector.metric_collector import snapshot_task, CollectMode

FLINK_HOST = config["servers"][0]["ip"]
FLINK_API = f"http://{FLINK_HOST}:8081"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@snapshot_task(
    cmd=(
            f"curl -s {FLINK_API}/jobs | jq -r '.jobs[0].id' | xargs -I{{}} curl -s {FLINK_API}/jobs/{{}}"
    ),
    tag="flink作业详情",
    collect_mode=CollectMode.ASYNC
)
def flink_job_detail(output: str) -> dict:
    try:
        job_detail = json.loads(output)
        vertices = job_detail.get("vertices", [])

        total_tasks = 0
        running_tasks = 0
        failed_tasks = 0
        parallelisms = []

        for v in vertices:
            p = v.get("parallelism", 0)
            status = v.get("status", "")
            total_tasks += p
            parallelisms.append(p)
            if status == "RUNNING":
                running_tasks += 1
            if status == "FAILED":
                failed_tasks += 1

        avg_parallelism = round(sum(parallelisms) / len(parallelisms), 2) if parallelisms else 0
        max_parallelism = max(parallelisms) if parallelisms else 0

        return {
            f"curl -s {FLINK_API}/jobs | jq -r '.jobs[0].id' ":
                {
                    "任务总数": total_tasks,
                    "运行中任务数": running_tasks,
                    "失败任务数": failed_tasks,
                    "平均并行度": avg_parallelism,
                    "最大并行度": max_parallelism,
                }
        }

    except Exception as e:
        logging.warning(f"解析 flink job detail 失败: {e}")
        return {}


@snapshot_task(
    cmd=(
            "curl -s {FLINK_API}/jobs | jq -r '.jobs[0].id' | xargs -I{{}} curl -s {FLINK_API}/jobs/{{}}/checkpoints"
    ),
    tag="flink checkpoint状态",
    collect_mode=CollectMode.ASYNC
)
def flink_checkpoint_status(output: str) -> dict:
    try:
        ckpt_info = json.loads(output)

        # 从 counts 字段获取失败次数
        failed_count = ckpt_info.get("counts", {}).get("failed", 0)

        # 获取最近一次完成的检查点信息 (注意：可能是 None/null)
        latest_completed = ckpt_info.get("latest", {}).get("completed")
        # 只有当 latest_completed 存在（不为 None）时才提取其数据
        if latest_completed is not None:
            latest_duration = latest_completed.get("duration", 0)
            latest_state_size = latest_completed.get("state_size", 0)
        else:
            # 如果没有完成的检查点，设置默认值
            latest_duration = 0
            latest_state_size = 0

        return {
            f"curl -s {FLINK_API}/jobs | jq -r '.jobs[0].id' ":
                {
                    "最近一次Checkpoint耗时(ms)": latest_duration,
                    "最近一次Checkpoint状态大小(bytes)": latest_state_size,
                    "Checkpoint失败次数": failed_count,
                }
        }
    except Exception as e:
        logging.warning(f"解析 flink checkpoint 信息失败: {e}")
        return {}


@snapshot_task(
    cmd=f"curl -s {FLINK_API}/jobs/overview",
    tag="flink作业总览",
    collect_mode=CollectMode.ASYNC
)
def flink_job_overview(output: str) -> dict:
    try:
        data = json.loads(output)
        jobs = data.get("jobs", [])
        return {
            f"curl -s {FLINK_API}/jobs/overview":
                {
                    "作业总数": len(jobs),
                    "运行中作业数": sum(1 for j in jobs if j.get("state") == "RUNNING"),
                    "失败作业数": sum(1 for j in jobs if j.get("state") == "FAILED"),
                }
        }
    except Exception as e:
        logging.warning(f"解析 flink jobs overview 失败: {e}")
        return {}


@snapshot_task(
    cmd=f"curl -s {FLINK_API}/taskmanagers",
    tag="flink资源使用",
    collect_mode=CollectMode.ASYNC
)
def flink_resource_usage(output: str) -> dict:
    try:
        data = json.loads(output)
        tms = data.get("taskmanagers", [])

        total_slots = sum(tm.get("slotsNumber", 0) for tm in tms)
        available_slots = sum(tm.get("slotsAvailable", 0) for tm in tms)
        total_heap = sum(tm.get("heapUsed", 0) for tm in tms)
        total_managed = sum(tm.get("managedMemoryUsed", 0) for tm in tms)

        return {
            "flink资源使用":
                {
                    "TaskManager数量": len(tms),
                    "总Slots数": total_slots,
                    "空闲Slots数": available_slots,
                    "Heap内存使用(MB)": round(total_heap / 1024 / 1024, 2),
                    "Managed内存使用(MB)": round(total_managed / 1024 / 1024, 2),
                }
        }
    except Exception as e:
        logging.warning(f"解析 flink taskmanagers 信息失败: {e}")
        return {}


@snapshot_task(
    cmd=(
            f"curl -s {FLINK_API}/jobs | jq -r '.jobs[0].id' | xargs -I{{}} curl -s {FLINK_API}/jobs/{{}}/backpressure"
    ),
    tag="flink反压指标",
    collect_mode=CollectMode.ASYNC
)
def flink_backpressure(output: str) -> dict:
    try:
        bp = json.loads(output)
        levels = bp.get("backpressure-levels", [])
        blocked = sum(1 for v in levels if v.get("backpressure-level") == "BLOCKED")
        ratio = f"{(blocked / len(levels)) * 100:.2f}%" if levels else "0%"
        return {
            f"curl -s {FLINK_API}/taskmanagers":
                {
                    "阻塞算子数量": blocked,
                    "Backpressure阻塞率": ratio
                }
        }
    except Exception as e:
        logging.warning(f"解析 flink backpressure 失败: {e}")
        return {}


# 核心吞吐量指标采集（确保返回所有关键指标）
@snapshot_task(
    cmd=(
            f"curl -s {FLINK_API}/jobs | jq -r '.jobs[0].id' | xargs -I{{}} curl -s "
            f"{FLINK_API}/jobs/{{}}/metrics?get="
            "numRecordsInPerSecond,"
            "numRecordsOutPerSecond,"
            "numBytesInPerSecond,"
            "numBytesOutPerSecond,"
            "latency,"
            "lastCheckpointSize"
    ),
    tag="flink_throughput_metrics",
    collect_mode=CollectMode.ASYNC
)
def flink_throughput_metrics(output: str) -> dict:
    """采集核心吞吐量指标并确保所有字段都有值"""
    try:
        metrics = json.loads(output)
        result = {
            "输入吞吐": 0.0,
            "输出吞吐": 0.0,
            "输入数据量": 0.0,
            "输出数据量": 0.0,
            "延迟指标": 0.0,
            "检查点大小": 0
        }

        for metric in metrics:
            metric_id = metric["id"]
            value = metric["value"]

            if "numRecordsInPerSecond" in metric_id:
                result["输入吞吐"] = float(value)
            elif "numRecordsOutPerSecond" in metric_id:
                result["输出吞吐"] = float(value)
            elif "numBytesInPerSecond" in metric_id:
                result["输入数据量"] = float(value)
            elif "numBytesOutPerSecond" in metric_id:
                result["输出数据量"] = float(value)
            elif "latency" in metric_id and "p99" in metric_id:
                result["延迟指标"] = float(value)
            elif "lastCheckpointSize" in metric_id:
                result["检查点大小"] = int(value)

        return {"flink_throughput_metrics": result}
    except Exception as e:
        logging.error(f"解析吞吐量指标失败: {e}")
        # 返回默认值而不是空字典
        return {"flink_throughput_metrics": {
            "输入吞吐": 0.0,
            "输出吞吐": 0.0,
            "输入数据量": 0.0,
            "输出数据量": 0.0,
            "延迟指标": 0.0,
            "检查点大小": 0
        }}


# 资源使用指标采集
@snapshot_task(
    cmd=(
            f"curl -s {FLINK_API}/taskmanagers | jq -r '.taskmanagers[0].id' | "
            f"xargs -I{{}} curl -s {FLINK_API}/taskmanagers/{{}}/metrics?get="
            "Status.JVM.CPU.Load,"
            "Status.JVM.Memory.Heap.Used"
    ),
    tag="flink_resource_usage",
    collect_mode=CollectMode.ASYNC
)
def flink_resource_usage(output: str) -> dict:
    """采集资源使用指标并确保返回有效数据"""
    try:
        metrics = json.loads(output)
        resource_data = {
            "CPU负载": 0.0,
            "堆内存使用": 0
        }

        for metric in metrics:
            metric_id = metric["id"]
            value = metric["value"]

            if "CPU.Load" in metric_id:
                resource_data["CPU负载"] = float(value) * 100  # 转换为百分比
            elif "Heap.Used" in metric_id:
                resource_data["堆内存使用"] = int(value)

        return {"flink_resource_usage": resource_data}
    except Exception as e:
        logging.error(f"解析资源指标失败: {e}")
        # 返回默认值而不是空字典
        return {"flink_resource_usage": {
            "CPU负载": 0.0,
            "堆内存使用": 0
        }}
