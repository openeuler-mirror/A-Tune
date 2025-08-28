from src.utils.collector.metric_collector import (
    snapshot_task,
    CollectMode,
)


@snapshot_task(
    cmd="redis-cli INFO",
    collect_mode=CollectMode.ASYNC,
    tag="Redis 实例的基本运行状态",
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
                "运行时间（秒）": (
                    info.get("运行时间（秒）") or int(value)
                    if key == "uptime_in_seconds"
                    else None
                ),
                "已连接客户端数": (
                    int(value)
                    if key == "connected_clients"
                    else info.get("已连接客户端数")
                ),
                "内存使用（字节）": (
                    int(value) if key == "used_memory" else info.get("内存使用（字节）")
                ),
                "每秒请求数（QPS）": (
                    int(value)
                    if key == "instantaneous_ops_per_sec"
                    else info.get("每秒请求数（QPS）")
                ),
                "总命中次数": (
                    int(value) if key == "keyspace_hits" else info.get("总命中次数")
                ),
                "总未命中次数": (
                    int(value) if key == "keyspace_misses" else info.get("总未命中次数")
                ),
                "阻塞客户端数": (
                    int(value) if key == "blocked_clients" else info.get("阻塞客户端数")
                ),
            }
        )
    cmd = "redis-cli INFO"
    result = {k: v for k, v in info.items() if v is not None}
    return {cmd: result}


@snapshot_task(
    cmd="redis-cli INFO commandstats",
    collect_mode=CollectMode.ASYNC,
    tag="Redis 命令的调用次数、耗时",
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
            "调用次数": int(values.get("calls", 0)),
            "总耗时（微秒）": int(values.get("usec", 0)),
            "平均耗时（微秒）": float(values.get("usec_per_call", 0)),
        }
    cmd = "redis-cli INFO commandstats"
    return {cmd: result}


@snapshot_task(
    cmd="redis-cli INFO stats",
    collect_mode=CollectMode.ASYNC,
    tag="Redis key的命中率",
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
    cmd = "redis-cli INFO commandstats"
    result = {"命中次数": hits, "未命中次数": misses, "命中率(%)": hit_rate}
    return {cmd: result}
