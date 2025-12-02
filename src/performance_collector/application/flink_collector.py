import json
import logging

from src.config import config
from src.utils.collector.metric_collector import snapshot_task, CollectMode
from src.utils.common import translate

FLINK_HOST = config["servers"][0]["listening_address"] if config["servers"][0]["listening_address"] else \
    config["servers"][0]["ip"]
FLINK_PORT = config["servers"][0]["listening_port"] if config["servers"][0]["listening_port"] else 8081
FLINK_API = f"http://{FLINK_HOST}:{FLINK_PORT}"

@snapshot_task(
    cmd=(
            f"curl -s {FLINK_API}/jobs | jq -r '.jobs[0].id' | xargs -I{{}} curl -s {FLINK_API}/jobs/{{}}"
    ),
    tag=translate("flink作业详情", "Flink Job Details"),
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
                    "total_tasks": total_tasks,
                    "running_tasks": running_tasks,
                    "failed_tasks": failed_tasks,
                    "avg_parallelism": avg_parallelism,
                    "max_parallelism": max_parallelism,
                }
        }

    except Exception as e:
        logging.warning(f"Failed to parse Flink job detail: {e}")
        return {}


@snapshot_task(
    cmd=(
            f"curl -s {FLINK_API}/jobs | jq -r '.jobs[0].id' | xargs -I{{}} curl -s {FLINK_API}/jobs/{{}}/checkpoints"
    ),
    tag=translate("flink checkpoint状态", "Flink Checkpoint Status"),
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
                    "latest_checkpoint_duration_ms": latest_duration,
                    "latest_checkpoint_state_size_bytes": latest_state_size,
                    "failed_checkpoint_count": failed_count,
                }
        }
    except Exception as e:
        logging.warning(f"Failed to parse Flink checkpoint information: {e}")
        return {}


@snapshot_task(
    cmd=f"curl -s {FLINK_API}/jobs/overview",
    tag=translate("flink作业总览", "Flink Job Overview"),
    collect_mode=CollectMode.ASYNC
)
def flink_job_overview(output: str) -> dict:
    try:
        data = json.loads(output)
        jobs = data.get("jobs", [])
        return {
            f"curl -s {FLINK_API}/jobs/overview":
                {
                    "total_jobs": len(jobs),
                    "running_jobs": sum(1 for j in jobs if j.get("state") == "RUNNING"),
                    "failed_jobs": sum(1 for j in jobs if j.get("state") == "FAILED"),
                }
        }
    except Exception as e:
        logging.warning(f"Failed to parse Flink jobs overview: {e}")
        return {}


@snapshot_task(
    cmd=f"curl -s {FLINK_API}/taskmanagers",
    tag=translate("flink资源使用", "Flink Resource Usage"),
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
            "flink_resource_usage":
                {
                    "taskmanager_count": len(tms),
                    "total_slots": total_slots,
                    "available_slots": available_slots,
                    "heap_memory_used_mb": round(total_heap / 1024 / 1024, 2),
                    "managed_memory_used_mb": round(total_managed / 1024 / 1024, 2),
                }
        }
    except Exception as e:
        logging.warning(f"Failed to parse Flink TaskManagers information: {e}")
        return {}


@snapshot_task(
    cmd=(
            f"curl -s {FLINK_API}/jobs | jq -r '.jobs[0].id' | xargs -I{{}} curl -s {FLINK_API}/jobs/{{}}/backpressure"
    ),
    tag=translate("flink反压指标", "Flink Backpressure Metrics"),
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
                    "blocked_operator_count": blocked,
                    "backpressure_ratio": ratio
                }
        }
    except Exception as e:
        logging.warning(f"Failed to parse Flink backpressure: {e}")
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
            "input_throughput": 0.0,
            "output_throughput": 0.0,
            "input_data_volume": 0.0,
            "output_data_volume": 0.0,
            "latency_metric": 0.0,
            "checkpoint_size": 0
        }

        for metric in metrics:
            metric_id = metric["id"]
            value = metric["value"]

            if "numRecordsInPerSecond" in metric_id:
                result["input_throughput"] = float(value)
            elif "numRecordsOutPerSecond" in metric_id:
                result["output_throughput"] = float(value)
            elif "numBytesInPerSecond" in metric_id:
                result["input_data_volume"] = float(value)
            elif "numBytesOutPerSecond" in metric_id:
                result["output_data_volume"] = float(value)
            elif "latency" in metric_id and "p99" in metric_id:
                result["latency_metric"] = float(value)
            elif "lastCheckpointSize" in metric_id:
                result["checkpoint_size"] = int(value)

        return {"flink_throughput_metrics": result}
    except Exception as e:
        logging.error(f"Failed to parse throughput metric: {e}")
        # 返回默认值而不是空字典
        return {"flink_throughput_metrics": {
            "input_throughput": 0.0,
            "output_throughput": 0.0,
            "input_data_volume": 0.0,
            "output_data_volume": 0.0,
            "latency_metric": 0.0,
            "checkpoint_size": 0
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
            "cpu_load": 0.0,
            "heap_memory_usage": 0
        }

        for metric in metrics:
            metric_id = metric["id"]
            value = metric["value"]

            if "CPU.Load" in metric_id:
                resource_data["cpu_load"] = float(value) * 100  # 转换为百分比
            elif "Heap.Used" in metric_id:
                resource_data["heap_memory_usage"] = int(value)

        return {"flink_resource_usage": resource_data}
    except Exception as e:
        logging.error(f"Failed to parse resource metrics: {e}")
        # 返回默认值而不是空字典
        return {"flink_resource_usage": {
            "cpu_load": 0.0,
            "heap_memory_usage": 0
        }}
