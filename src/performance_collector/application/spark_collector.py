import json
import logging

import requests

from src.config import config
from src.utils.common import translate
from src.utils.collector.metric_collector import (
    period_task,
    snapshot_task,
    CollectMode,
)

SPARK_HOST = config["servers"][0]["listening_address"] if config["servers"][0]["listening_address"] else \
    config["servers"][0]["ip"]
SPARK_PORT = config["servers"][0]["listening_port"] if config["servers"][0]["listening_port"] else 18080

SPARK_HISTORY_SERVER = f"http://{SPARK_HOST}:{SPARK_PORT}"
SAMPLE_INTERVAL = 60
SAMPLE_COUNT = 2
DURATION = SAMPLE_INTERVAL * (SAMPLE_COUNT - 1)

@snapshot_task(
    cmd="curl -s {}/api/v1/applications | jq -r '.[0].id'".format(SPARK_HISTORY_SERVER),
    tag=translate("spark作业信息", "Spark job information"),
    collect_mode=CollectMode.ASYNC
)
def spark_job_info(app_id: str) -> dict:
    app_id = app_id.strip().strip('"')
    if not app_id:
        return {}
    try:
        cmd = f"{SPARK_HISTORY_SERVER}/api/v1/applications/{app_id}/jobs"
        resp = requests.get(cmd, timeout=10)
        jobs = resp.json()
        total_jobs = len(jobs)
        running_jobs = sum(1 for job in jobs if job["status"] == "RUNNING")
        failed_jobs = sum(1 for job in jobs if job["status"] == "FAILED")
        total_tasks = sum(job.get("numTasks") for job in jobs)
        total_failed_tasks = sum(job.get("numFailedTasks") for job in jobs)
        total_killed_tasks = sum(job.get("numKilledTasks") for job in jobs)
        total_skipped_tasks = sum(job.get("numSkippedTasks") for job in jobs)
        total_completed_stages = sum(job.get("numCompletedStages") for job in jobs)
        result = {
            "total_jobs": total_jobs,
            "running_jobs": running_jobs,
            "failed_jobs": failed_jobs,
            "total_tasks": total_tasks,
            "failed_tasks": total_failed_tasks,
            "killed_tasks": total_killed_tasks,
            "skipped_tasks": total_skipped_tasks,
            "completed_stages": total_completed_stages
        }
        return {cmd: result}

    except Exception as e:
        logging.warning(f"Failed to get job info: {e}")
        return {}


@snapshot_task(
    cmd="curl -s {}/api/v1/applications | jq -r '.[0].id'".format(SPARK_HISTORY_SERVER),
    tag=translate("spark阶段信息", "Spark stage information"),
    collect_mode=CollectMode.ASYNC
)
def spark_stage_info(app_id: str) -> dict:
    app_id = app_id.strip().strip('"')  # 去掉引号与换行
    if not app_id:
        return {}

    try:
        cmd = f"{SPARK_HISTORY_SERVER}/api/v1/applications/{app_id}/stages"
        resp = requests.get(cmd, timeout=10)
        stages = resp.json()
        total_stages = len(stages)
        total_tasks = sum(s.get("numTasks", 0) for s in stages)
        total_executor_time = sum(s.get("executorRunTime", 0) for s in stages)
        total_gc_time = sum(s.get("jvmGcTime", 0) for s in stages)
        total_mem_spill = sum(s.get("memoryBytesSpilled", 0) for s in stages)
        total_disk_spill = sum(s.get("diskBytesSpilled", 0) for s in stages)
        failed_stages = sum(1 for s in stages if s["status"] == "FAILED")
        result = {
            "total_stages": total_stages,
            "failed_stages": failed_stages,
            "total_tasks": total_tasks,
            "total_executor_time_ms": total_executor_time,
            "total_gc_time_ms": total_gc_time,
            "gc_ratio": f"{(total_gc_time / total_executor_time) * 100:.2f}%" if total_executor_time else "0%",
            "total_memory_spill": total_mem_spill,
            "total_disk_spill": total_disk_spill
        }
        return {cmd: result}
    except Exception as e:
        logging.warning(f"Failed to get stage info: {e}")
        return {}


@period_task(
    cmd="curl -s {}/api/v1/applications/$(curl -s {}/api/v1/applications | jq -r '.[0].id')/executors".format(
        SPARK_HISTORY_SERVER, SPARK_HISTORY_SERVER
    ),
    tag=translate("spark执行器信息", "Spark executor information"),
    collect_mode=CollectMode.ASYNC,
    delay=0,
    sample_count=SAMPLE_COUNT,
    interval=SAMPLE_INTERVAL
)
def spark_executor_info(output: list[str]) -> dict:
    if len(output) < 2:
        return {}
    try:
        cmd = "curl -s {}/api/v1/applications/$(curl -s {}/api/v1/applications | jq -r '.[0].id')/executors".format(
            SPARK_HISTORY_SERVER, SPARK_HISTORY_SERVER
        )
        data1 = json.loads(output[0])
        data2 = json.loads(output[1])

        def agg(executors):
            filtered = [e for e in executors if e.get("id") != "driver"]
            return {
                "executor_count": len(filtered),
                "total_cores": sum(e.get("totalCores", 0) for e in filtered),
                "total_tasks": sum(e.get("totalTasks", 0) for e in filtered),
                "failed_tasks": sum(e.get("failedTasks", 0) for e in filtered),
                "total_gc_time": sum(e.get("totalGCTime", 0) for e in filtered),
            }

        metrics1 = agg(data1)
        metrics2 = agg(data2)
        delta_tasks = max(0, metrics2["total_tasks"] - metrics1["total_tasks"])
        delta_gc = max(0, metrics2["total_gc_time"] - metrics1["total_gc_time"])
        avg_tasks_per_executor = (
            delta_tasks // metrics2["executor_count"]
            if metrics2["executor_count"] > 0 else 0
        )
        result = {
            f"{DURATION}s内任务总量": metrics1["total_tasks"] + metrics2["total_tasks"],
            f"{DURATION}s内GC总耗时(ms)": metrics1["total_gc_time"] + metrics2["total_gc_time"],
            f"{DURATION}s内任务增长量": delta_tasks,
            f"{DURATION}s内GC总耗时增长量(ms)": delta_gc,
            "Executor数": metrics2["executor_count"],
            "总核数": metrics2["total_cores"],
            "失败任务数": metrics2["failed_tasks"],
            f"{DURATION}s内平均每Executor任务增长数": avg_tasks_per_executor
        }
        return {cmd: result}
    except Exception as e:
        logging.error(f"Failed to parse executor metrics: {e}")
        return {}
