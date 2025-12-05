import logging
import pandas as pd
from io import StringIO
from src.utils.common import translate
from src.utils.collector.metric_collector import (
    period_task,
    snapshot_task,
    CollectMode,
)

GAUSS_INTERVAL = 60

# -------------------- 1. 后台写入与检查点（两次采样） --------------------
@period_task(
    # cmd='gsql -p 17777 -d tpcc1000w_ustore  -A -F , -c "SELECT * FROM pg_stat_bgwriter;"',
    cmd='source ~/.bashrc && gsql -d tpcc -p 11111 -c "SELECT * FROM pg_stat_bgwriter;"',
    collect_mode=CollectMode.ASYNC,
    tag=translate("GaussDB后台写入与检查点", "GaussDB Background Writing and Checkpointing"),
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
        "checkpoints_timed": "scheduled_checkpoints",
        "checkpoints_req": "requested_checkpoints",
        "checkpoint_write_time": "checkpoint_write_time_ms",
        "checkpoint_sync_time": "checkpoint_sync_time_ms",
        "buffers_checkpoint": "checkpoint_pages_written",
        "buffers_clean": "background_clean_pages",
        "maxwritten_clean": "background_clean_overflows",
        "buffers_backend": "backend_write_pages",
        "buffers_backend_fsync": "backend_fsync_count",
        "buffers_alloc": "new_buffer_pages_allocated"
    }
    result = {}
    for key, label in mapping.items():
        try:
            delta = int(r2.get(key, 0)) - int(r1.get(key, 0))
        except (ValueError, TypeError):
            delta = 0
        result[f"{GAUSS_INTERVAL // 60}分钟内{label}"] = max(delta, 0)
    print("GaussDB后台写入与检查点:", result)
    return result


# -------------------- 2. 事务与IO（两次采样） --------------------
@period_task(
    cmd='''source ~/.bashrc && gsql -p 11111 -d tpcc  -A -F , -c "
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
    res = {}
    for col in ("commits", "rollbacks", "blks_read", "blks_hit", "tup_returned", "tup_fetched"):
        try:
            delta = int(r2[col]) - int(r1[col])
        except (ValueError, TypeError):
            delta = 0
        res[f"{GAUSS_INTERVAL // 60}分钟内{col}"] = max(delta, 0)

    # 计算命中率
    hit_delta = res.get(f"{GAUSS_INTERVAL // 60}分钟内blks_hit", 0)
    read_delta = res.get(f"{GAUSS_INTERVAL // 60}分钟内blks_read", 0)
    res[f"{GAUSS_INTERVAL // 60}分钟内Buffer命中率"] = (
        round(hit_delta * 100 / (hit_delta + read_delta),
              2) if (hit_delta + read_delta) else 0
    )
    return res


# -------------------- 3. 会话信息（实时快照） --------------------
@snapshot_task(
    cmd='''source ~/.bashrc && gsql -p 11111 -d tpcc  -A -F , -c "
SELECT datname, state, waiting, enqueue
FROM pg_stat_activity;"''',
    tag=translate("GaussDB会话信息", "GaussDB Session Information"),
)
def gauss_activity_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {
        "datname": "database_name",
        "state": "connection_state",
        "waiting": "is_waiting",
        "enqueue": "enqueue_lock_info"
    }
    return {
        "session_information": [
            {mapping.get(k, k): v for k, v in row.items()}
            for _, row in df.iterrows()
        ]
    }


# -------------------- 4. 锁信息（实时快照） --------------------
@snapshot_task(
    cmd='source ~/.bashrc && gsql -p 11111 -d tpcc  -A -F , -c "SELECT mode, granted, COUNT(*) AS count FROM pg_locks GROUP BY mode, granted;"',
    collect_mode=CollectMode.ASYNC,
    tag=translate("GaussDB锁信息", "GaussDB Lock Information",)
)
def gauss_locks_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {
        "mode": "lock_mode",
        "granted": "is_granted",
        "count": "lock_count"
    }
    return {
        "lock_infomation": [
            {mapping.get(k, k): v for k, v in row.items()} for _, row in df.iterrows()
        ]
    }


# -------------------- 5. 数据库级统计（实时快照） --------------------
@snapshot_task(
    cmd='''source ~/.bashrc && gsql -p 11111 -d tpcc  -A -F , -c "SELECT datname, numbackends, xact_commit, xact_rollback,
        blks_read, blks_hit, pg_database_size(datname) AS db_size_bytes
        FROM pg_stat_database WHERE datname NOT IN ('template0', 'template1');"''',
    collect_mode=CollectMode.ASYNC,
    tag=translate("GaussDB数据库级指标", "GaussDB Database-Level Metrics"),
)
def gauss_database_snapshot_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {
        "datname": "database_name",
        "numbackends": "connection_count",
        "xact_commit": "committed_transactions",
        "xact_rollback": "rolled_back_transactions",
        "blks_read": "disk_blocks_read",
        "blks_hit": "buffer_hit_blocks",
        "db_size_bytes": "database_size_bytes"
    }
    return {
        "database_statistics": [
            {mapping.get(k, k): v for k, v in row.items()} for _, row in df.iterrows()
        ]
    }


# -------------------- 6. 内存使用（实时快照） --------------------
@snapshot_task(
    cmd='''source ~/.bashrc && gsql -p 11111 -d tpcc -A -F , -c "
        SELECT
            'localhost' AS node_name,
            SUM(usedsize) AS dynamic_used_memory_bytes,
            MAX(usedsize) AS dynamic_peak_memory_bytes
        FROM gs_session_memory_detail;"''',
    collect_mode=CollectMode.ASYNC,
    tag=translate("GaussDB内存使用", "GaussDB Memory Usage"),
)
def gauss_memory_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {
        "node_name": "node_name",
        "dynamic_used_memory": "dynamic_used_memory",
        "dynamic_peak_memory": "dynamic_peak_memory",
    }
    return {
        "memory_infomation": [
            {mapping.get(k, k): v for k, v in row.items()} for _, row in df.iterrows()
        ]
    }
