import logging
import requests
import json
from src.utils.collector.metric_collector import (
    period_task,
    snapshot_task,
    CollectMode,
)
from src.config import config

HOST_IP = config["servers"][0]["ip"]
SPARK_HISTORY_SERVER = f"http://{HOST_IP}:18080"
SAMPLE_INTERVAL = 60
SAMPLE_COUNT = 2
DURATION = SAMPLE_INTERVAL * (SAMPLE_COUNT - 1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@snapshot_task(
    cmd="curl -s {}/api/v1/applications | jq -r '.[0].id'".format(SPARK_HISTORY_SERVER),
    tag="spark作业信息",
    collect_mode=CollectMode.ASYNC
)
def spark_job_info(app_id: str) -> dict:
    app_id = app_id.strip().strip('"')
    if not app_id:
        return {}
    try:
        resp = requests.get(f"{SPARK_HISTORY_SERVER}/api/v1/applications/{app_id}/jobs", timeout=10)
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
            "Job总数": total_jobs,
            "运行中Job数": running_jobs,
            "失败Job数": failed_jobs,
            "任务总数": total_tasks,
            "失败Task总数": total_failed_tasks,
            "被杀Task总数": total_killed_tasks,
            "跳过Task总数": total_skipped_tasks,
            "已完成Stage总数": total_completed_stages,
        }
        return {"spark作业信息": result}

    except Exception as e:
        logging.warning(f"获取 job 信息失败: {e}")
        return {}


@snapshot_task(
    cmd="curl -s {}/api/v1/applications | jq -r '.[0].id'".format(SPARK_HISTORY_SERVER),
    tag="spark阶段信息",
    collect_mode=CollectMode.ASYNC
)
def spark_stage_info(app_id: str) -> dict:
    app_id = app_id.strip().strip('"')  # 去掉引号与换行
    if not app_id:
        return {}

    try:
        resp = requests.get(f"{SPARK_HISTORY_SERVER}/api/v1/applications/{app_id}/stages", timeout=10)
        stages = resp.json()
        total_stages = len(stages)
        total_tasks = sum(s.get("numTasks", 0) for s in stages)
        total_executor_time = sum(s.get("executorRunTime", 0) for s in stages)
        total_gc_time = sum(s.get("jvmGcTime", 0) for s in stages)
        total_mem_spill = sum(s.get("memoryBytesSpilled", 0) for s in stages)
        total_disk_spill = sum(s.get("diskBytesSpilled", 0) for s in stages)
        failed_stages = sum(1 for s in stages if s["status"] == "FAILED")
        result = {
            "Stage总数": total_stages,
            "失败Stage数": failed_stages,
            "总任务数": total_tasks,
            "总执行时间(ms)": total_executor_time,
            "总GC时间(ms)": total_gc_time,
            "GC占比": f"{(total_gc_time / total_executor_time) * 100:.2f}%" if total_executor_time else "0%",
            "总Memory Spill": total_mem_spill,
            "总Disk Spill": total_disk_spill,
        }
        return {"spark阶段信息": result}
    except Exception as e:
        logging.warning(f"获取 stage 信息失败: {e}")
        return {}


@period_task(
    cmd="curl -s {}/api/v1/applications/$(curl -s {}/api/v1/applications | jq -r '.[0].id')/executors".format(
        SPARK_HISTORY_SERVER, SPARK_HISTORY_SERVER
    ),
    tag="spark执行器信息",
    collect_mode=CollectMode.ASYNC,
    delay=0,
    sample_count=SAMPLE_COUNT,
    interval=SAMPLE_INTERVAL
)
def spark_executor_info(output: list[str]) -> dict:
    if len(output) < 2:
        return {}
    try:
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
        return {"spark执行器信息": result}
    except Exception as e:
        logging.error(f"解析 executor 指标失败: {e}")
        return {}
