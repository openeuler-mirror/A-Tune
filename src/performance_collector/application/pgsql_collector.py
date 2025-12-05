import logging
from io import StringIO

import pandas as pd
from src.utils.common import translate
from src.utils.collector.metric_collector import (
    period_task,
    snapshot_task,
    CollectMode,
)

BIG_WRITER_COLLECT_INTERVAL = 180


# 采集5分钟内数据
@period_task(
    cmd="su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT * FROM pg_stat_bgwriter;'\"",
    collect_mode=CollectMode.ASYNC,
    tag=translate("pgsql缓存指标", "pgsql cache metrics"),
    delay=0,
    sample_count=2,
    interval=BIG_WRITER_COLLECT_INTERVAL
)
def pg_stat_bgwriter_parser(output: list[str]) -> dict:
    if len(output) < 2:
        return {}  # 需要两次采样才能计算差值

    df1 = pd.read_csv(StringIO(output[0]))
    df2 = pd.read_csv(StringIO(output[1]))

    if df1.empty or df2.empty:
        return {}

    row1 = df1.iloc[0].to_dict()
    row2 = df2.iloc[0].to_dict()

    mapping = {
        "checkpoints_timed": "scheduled_checkpoints",
        "checkpoints_req": "requested_checkpoints", 
        "checkpoint_write_time": "checkpoint_write_time_ms",
        "checkpoint_sync_time": "checkpoint_sync_time_ms",
        "buffers_checkpoint": "checkpoint_pages_written",
        "buffers_clean": "background_clean_pages",
        "maxwritten_clean": "maxwritten_trigger_count",
        "buffers_backend": "backend_write_pages",
        "buffers_backend_fsync": "backend_fsync_count",
        "buffers_alloc": "new_buffer_pages_allocated"
    }

    result = {}
    for key, label in mapping.items():
        new_label = f"{BIG_WRITER_COLLECT_INTERVAL // 60}分钟内{label}"

        old_val = row1.get(key, 0)
        new_val = row2.get(key, 0)

        try:
            delta = int(new_val) - int(old_val)
        except (ValueError, TypeError):
            delta = 0  # 如果解析失败就默认 0

        result[new_label] = max(delta, 0)  # 防止 PostgreSQL 重启导致出现负值
    cmd = "su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT * FROM pg_stat_bgwriter;'\""
    return {cmd: result}


@snapshot_task(
    cmd="su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT datname, state, wait_event_type, wait_event FROM pg_stat_activity;'\"",
    collect_mode=CollectMode.ASYNC,
    tag=translate("pgsql数据库连接信息", "pgsql Database Connection Information"),
)
def pg_stat_activity_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {
        "datname": "database_name",
        "state": "connection_state", 
        "wait_event_type": "wait_event_type",
        "wait_event": "wait_event"
    }
    result = []
    for _, row in df.iterrows():
        raw = dict(row)
        result.append({mapping.get(k, k): v for k, v in raw.items()})
    cmd = "su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT datname, state, wait_event_type, wait_event FROM pg_stat_activity;'\""
    return {cmd: result}


@snapshot_task(
    cmd="su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT datname, numbackends, xact_commit, xact_rollback, blks_read, blks_hit FROM pg_stat_database;'\"",
    collect_mode=CollectMode.ASYNC,
    tag=translate("pgsql数据库指标", "pgsql Database Metrics"),
)
def pg_stat_database_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {
        "datname": "database_name",
        "numbackends": "connection_count",
        "xact_commit": "committed_transactions",
        "xact_rollback": "rolled_back_transactions",
        "blks_read": "disk_blocks_read",
        "blks_hit": "cache_hits",
    }
    result = []
    for _, row in df.iterrows():
        raw = dict(row)
        result.append({mapping.get(k, k): v for k, v in raw.items()})
    cmd = "su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT datname, numbackends, xact_commit, xact_rollback, blks_read, blks_hit FROM pg_stat_database;'\""
    return {cmd: result}


@snapshot_task(
    cmd="su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT mode, granted, COUNT(*) as count FROM pg_locks GROUP BY mode, granted;'\"",
    collect_mode=CollectMode.ASYNC,
    tag=translate("pgsql锁指标", "pgsql Lock Metrics"),
)
def pg_locks_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {
        "mode": "lock_mode",
        "granted": "is_granted", 
        "count": "lock_count"
    }
    result = []
    for _, row in df.iterrows():
        raw = dict(row)
        result.append({mapping.get(k, k): v for k, v in raw.items()})
    cmd = "su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT mode, granted, COUNT(*) as count FROM pg_locks GROUP BY mode, granted;'\""
    return {cmd: result}
