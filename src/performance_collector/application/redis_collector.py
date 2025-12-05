from src.utils.common import translate
from src.utils.collector.metric_collector import (
    snapshot_task,
    CollectMode,
)


@snapshot_task(
    cmd="redis-cli INFO",
    collect_mode=CollectMode.ASYNC,
    tag=translate("Redis 实例的基本运行状态", "Basic operational status of Redis instances"),
)
def parse_redis_info(info_output: str) -> dict:
    """解析 redis-cli info 命令输出为带中文 key 的字典"""
    info = {}
    for line in info_output.strip().splitlines():
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.strip().split(":", 1)
        info.update(
            {
                "uptime_in_seconds": (
                    info.get("uptime_in_seconds") or int(value)
                    if key == "uptime_in_seconds"
                    else None
                ),
                "connected_clients": (
                    int(value)
                    if key == "connected_clients"
                    else info.get("connected_clients")
                ),
                "used_memory": (
                    int(value) if key == "used_memory" else info.get("used_memory")
                ),
                "instantaneous_ops_per_sec": (
                    int(value)
                    if key == "instantaneous_ops_per_sec"
                    else info.get("instantaneous_ops_per_sec")
                ),
                "keyspace_hits": (
                    int(value) if key == "keyspace_hits" else info.get("keyspace_hits")
                ),
                "keyspace_misses": (
                    int(value) if key == "keyspace_misses" else info.get("keyspace_misses")
                ),
                "blocked_clients": (
                    int(value) if key == "blocked_clients" else info.get("blocked_clients")
                ),
            }
        )
    cmd = "redis-cli INFO"
    result = {k: v for k, v in info.items() if v is not None}
    return {cmd: result}


@snapshot_task(
    cmd="redis-cli INFO commandstats",
    collect_mode=CollectMode.ASYNC,
    tag=translate("Redis 命令的调用次数、耗时", "Number of Redis command calls and their execution time"),
)
def parse_commandstats(commandstats_output: str) -> dict:
    """解析 commandstats 为每个命令调用次数和平均耗时"""
    result = {}
    for line in commandstats_output.strip().splitlines():
        if not line.startswith("cmdstat_"):
            continue
        parts = line.split(":")
        cmd = parts[0].replace("cmdstat_", "")
        values = dict(item.split("=") for item in parts[1].split(","))
        result[cmd] = {
            "command_calls": int(values.get("calls", 0)),
            "total_time_microseconds": int(values.get("usec", 0)),
            "avg_time_microseconds": float(values.get("usec_per_call", 0))
        }
    cmd = "redis-cli INFO commandstats"
    return {cmd: result}


@snapshot_task(
    cmd="redis-cli INFO stats",
    collect_mode=CollectMode.ASYNC,
    tag=translate("Redis key的命中率", "Hit rate of Redis keys"),
)
def parse_hit_rate_from_info_stats(info_stats_output: str) -> dict:
    """
    从 redis-cli INFO stats 的输出字符串中解析 key 命中率。
    参数:
        info_stats_output (str): INFO stats 命令的原始输出
    返回:
        dict: {'命中次数': ..., '未命中次数': ..., '命中率(%)': ...}
    """
    hits = 0
    misses = 0

    for line in info_stats_output.strip().splitlines():
        line = line.strip()
        if line.startswith("keyspace_hits:"):
            hits = int(line.split(":")[1])
        elif line.startswith("keyspace_misses:"):
            misses = int(line.split(":")[1])

    total = hits + misses
    hit_rate = round(hits / total * 100, 2) if total else 0.0
    cmd = "redis-cli INFO stats"
    result = {"cache_hits": hits,  "cache_misses": misses, "hit_rate_percent": hit_rate}
    return {cmd: result}
