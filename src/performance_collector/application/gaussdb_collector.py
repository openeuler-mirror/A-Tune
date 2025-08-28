import logging
from io import StringIO

import pandas as pd

from src.utils.collector.metric_collector import (
    period_task,
    snapshot_task,
    CollectMode,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

GAUSS_INTERVAL = 180


# -------------------- 1. 后台写入与检查点（两次采样） --------------------
@period_task(
    cmd='gsql -d tpch  -A -F , -c "SELECT * FROM pg_stat_bgwriter;"',
    collect_mode=CollectMode.ASYNC,
    tag="GaussDB后台写入与检查点",
    delay=0,
    sample_count=2,
    interval=GAUSS_INTERVAL,
)
def gauss_bgwriter_parser(output: list[str]) -> dict:
    if len(output) < 2:
        return {}
    df1 = pd.read_csv(StringIO(output[0]))
    df2 = pd.read_csv(StringIO(output[1]))
    if df1.empty or df2.empty:
        return {}

    r1, r2 = df1.iloc[0].to_dict(), df2.iloc[0].to_dict()
    mapping = {
        "checkpoints_timed": "定时检查点",
        "checkpoints_req": "请求检查点",
        "checkpoint_write_time": "检查点写入耗时(ms)",
        "checkpoint_sync_time": "检查点同步耗时(ms)",
        "buffers_checkpoint": "检查点写出页数",
        "buffers_clean": "后台清理写出页数",
        "maxwritten_clean": "后台清理超限次数",
        "buffers_backend": "后端写出页数",
        "buffers_backend_fsync": "后端 fsync 次数",
        "buffers_alloc": "分配新缓冲区页数",
    }
    result = {}
    for key, label in mapping.items():
        try:
            delta = int(r2.get(key, 0)) - int(r1.get(key, 0))
        except (ValueError, TypeError):
            delta = 0
        result[f"{GAUSS_INTERVAL // 60}分钟内{label}"] = max(delta, 0)
    cmd = '''gsql -d tpch  -A -F , -c "SELECT * FROM pg_stat_bgwriter;"'''
    return {cmd: result}


# -------------------- 2. 事务与IO（两次采样） --------------------
@period_task(
    cmd='''gsql -d tpch  -A -F , -c "
    SELECT sum(xact_commit)   as commits,
        sum(xact_rollback) as rollbacks,
        sum(blks_read)     as blks_read,
        sum(blks_hit)      as blks_hit,
        sum(tup_returned)  as tup_returned,
        sum(tup_fetched)   as tup_fetched
    FROM pg_stat_database;"''',
    collect_mode=CollectMode.ASYNC,
    tag="GaussDB事务与IO",
    delay=0,
    sample_count=2,
    interval=GAUSS_INTERVAL,
)
def gauss_dbstat_parser(output: list[str]) -> dict:
    if len(output) < 2:
        return {}
    df1 = pd.read_csv(StringIO(output[0]))
    df2 = pd.read_csv(StringIO(output[1]))
    if df1.empty or df2.empty:
        return {}

    r1, r2 = df1.iloc[0].to_dict(), df2.iloc[0].to_dict()
    result = {}
    for col in ("commits", "rollbacks", "blks_read", "blks_hit", "tup_returned", "tup_fetched"):
        try:
            delta = int(r2[col]) - int(r1[col])
        except (ValueError, TypeError):
            delta = 0
        result[f"{GAUSS_INTERVAL // 60}分钟内{col}"] = max(delta, 0)

    # 计算命中率
    hit_delta = result[f"{GAUSS_INTERVAL // 60}分钟内blks_hit"]
    read_delta = result[f"{GAUSS_INTERVAL // 60}分钟内blks_read"]
    result[f"{GAUSS_INTERVAL // 60}分钟内Buffer命中率"] = (
        round(hit_delta * 100 / (hit_delta + read_delta), 2) if (hit_delta + read_delta) else 0
    )
    cmd = '''gsql -d tpch  -A -F , -c "
            SELECT sum(xact_commit)   as commits,
                sum(xact_rollback) as rollbacks,
                sum(blks_read)     as blks_read,
                sum(blks_hit)      as blks_hit,
                sum(tup_returned)  as tup_returned,
                sum(tup_fetched)   as tup_fetched
            FROM pg_stat_database;"'''
    return {cmd: result}


# -------------------- 3. 会话信息（实时快照） --------------------
@snapshot_task(
    cmd='''gsql -d tpch  -A -F , -c "
SELECT datname, state, waiting, enqueue
FROM pg_stat_activity;"''',
    collect_mode=CollectMode.ASYNC,
    tag="GaussDB会话信息",
)
def gauss_activity_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {
        "datname": "数据库名",
        "state": "连接状态",
        "waiting": "是否等待",
        "enqueue": "排队/锁信息",
    }
    cmd = '''gsql -d tpch  -A -F , -c "SELECT datname, state, waiting, enqueueFROM pg_stat_activity;"'''
    result = [
        {mapping.get(k, k): v for k, v in row.items()}
        for _, row in df.iterrows()
    ]
    return {cmd: result}


# -------------------- 4. 锁信息（实时快照） --------------------
@snapshot_task(
    cmd='''gsql -d tpch  -A -F , -c "SELECT mode, granted, COUNT(*) AS count FROM pg_locks GROUP BY mode, granted;"''',
    collect_mode=CollectMode.ASYNC,
    tag="GaussDB锁信息",
)
def gauss_locks_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {"mode": "锁模式", "granted": "是否已授予", "count": "锁数量"}
    cmd = '''gsql -d tpch  -A -F , -c "SELECT mode, granted, COUNT(*) AS count FROM pg_locks GROUP BY mode, granted;"'''
    result = [
        {mapping.get(k, k): v for k, v in row.items()} for _, row in df.iterrows()
    ]
    return {cmd: result}


# -------------------- 5. 数据库级统计（实时快照） --------------------
@snapshot_task(
    cmd='''gsql -d tpch  -A -F , -c "SELECT datname, numbackends, xact_commit, xact_rollback,
        blks_read, blks_hit, pg_database_size(datname) AS db_size_bytes
        FROM pg_stat_database WHERE datname NOT IN ('template0', 'template1');"''',
    collect_mode=CollectMode.ASYNC,
    tag="GaussDB数据库级指标",
)
def gauss_database_snapshot_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {
        "datname": "数据库名",
        "numbackends": "连接数",
        "xact_commit": "提交事务数",
        "xact_rollback": "回滚事务数",
        "blks_read": "磁盘读块数",
        "blks_hit": "缓冲命中块数",
        "db_size_bytes": "数据库大小(Bytes)",
    }
    cmd = '''gsql -d tpch  -A -F , -c "SELECT datname, numbackends, xact_commit, xact_rollback,
        blks_read, blks_hit, pg_database_size(datname) AS db_size_bytes
        FROM pg_stat_database WHERE datname NOT IN ('template0', 'template1');"'''
    result = [
        {mapping.get(k, k): v for k, v in row.items()} for _, row in df.iterrows()
    ]

    return {cmd: result}


# -------------------- 6. 内存使用（实时快照） --------------------
@snapshot_task(
    cmd='''gsql -d tpch -A -F , -c "
        SELECT
            'localhost' AS node_name,
            SUM(usedsize) AS dynamic_used_memory_bytes,
            MAX(usedsize) AS dynamic_peak_memory_bytes
        FROM gs_session_memory_detail;"''',
    collect_mode=CollectMode.ASYNC,
    tag="GaussDB内存使用",
)
def gauss_memory_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {
        "node_name": "节点名",
        "dynamic_used_memory": "已使用动态内存(MB)",
        "dynamic_peak_memory": "动态内存峰值(MB)",
    }
    cmd = '''gsql -d tpch -A -F , -c "
        SELECT
            'localhost' AS node_name,
            SUM(usedsize) AS dynamic_used_memory_bytes,
            MAX(usedsize) AS dynamic_peak_memory_bytes
        FROM gs_session_memory_detail;"'''
    result = [
        {mapping.get(k, k): v for k, v in row.items()} for _, row in df.iterrows()
    ]
    return {cmd: result}
