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

BIG_WRITER_COLLECT_INTERVAL = 180


# 采集5分钟内数据
@period_task(
    cmd="su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT * FROM pg_stat_bgwriter;'\"",
    collect_mode=CollectMode.ASYNC,
    tag="pgsql缓存指标",
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
        "checkpoints_timed": "定时检查点次数",
        "checkpoints_req": "请求检查点次数",
        "checkpoint_write_time": "检查点写入耗时(ms)",
        "checkpoint_sync_time": "检查点同步耗时(ms)",
        "buffers_checkpoint": "检查点写出页数",
        "buffers_clean": "后台清理写出页数",
        "maxwritten_clean": "超限触发写出次数",
        "buffers_backend": "后端写出页数",
        "buffers_backend_fsync": "后端 fsync 次数",
        "buffers_alloc": "分配新缓冲区页数",
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
    tag="pgsql数据库连接信息",
)
def pg_stat_activity_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {
        "datname": "数据库名",
        "state": "连接状态",
        "wait_event_type": "等待事件类型",
        "wait_event": "等待事件",
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
    tag="pgsql数据库指标",
)
def pg_stat_database_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {
        "datname": "数据库名",
        "numbackends": "连接数",
        "xact_commit": "提交事务数",
        "xact_rollback": "回滚事务数",
        "blks_read": "磁盘读块数",
        "blks_hit": "缓冲命中块数",
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
    tag="pgsql锁指标",
)
def pg_locks_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    mapping = {"mode": "锁模式", "granted": "是否已授予", "count": "锁数量"}
    result = []
    for _, row in df.iterrows():
        raw = dict(row)
        result.append({mapping.get(k, k): v for k, v in raw.items()})
    cmd = "su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT mode, granted, COUNT(*) as count FROM pg_locks GROUP BY mode, granted;'\""
    return {cmd: result}
