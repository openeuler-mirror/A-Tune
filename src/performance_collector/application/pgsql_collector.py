import re
import logging
import pandas as pd
from io import StringIO

from src.utils.shell_execute import cmd_pipeline

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


#
@cmd_pipeline(
    cmd="su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT * FROM pg_stat_bgwriter;'\"",
    tag="pgsql",
    parallel=True,
)
def pg_stat_bigwriter_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    if not df.empty:
        return dict(zip(df.columns, df.iloc[0]))
    else:
        return {}


# pgsql连接数信息
@cmd_pipeline(
    cmd="su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT count(*) FROM pg_stat_activity;'\"",
    tag="pgsql",
    parallel=True,
)
def pg_stat_activity_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    if not df.empty:
        stat_activity = dict(zip(df.columns, df.iloc[0]))
    else:
        stat_activity = {}
    return {
        "当前活跃连接数": stat_activity["count"]
    }


@cmd_pipeline(
    cmd="su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT round(sum(blks_hit)*100/sum(blks_hit+blks_read),2) AS cache_hit_ratio FROM pg_stat_database;'\"",
    tag="pgsql",
    parallel=True,
)
def pg_buffer_cache_hit_ratio_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    if not df.empty:
        cache_hit_ratio = dict(zip(df.columns, df.iloc[0]))
    else:
        cache_hit_ratio = {}
    return {"Buffer缓存命中率": cache_hit_ratio["cache_hit_ratio"]}


@cmd_pipeline(
    cmd="su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT pg_current_wal_lsn();'\"",
    tag="pgsql",
    parallel=True,
)
def pg_buffer_cache_hit_ratio_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    if not df.empty:
        return dict(zip(df.columns, df.iloc[0]))
    else:
        return {}


@cmd_pipeline(
    cmd="su - postgres -c \"/usr/local/pgsql/bin/psql --csv -c 'SELECT * FROM pg_locks WHERE granted = false;'\"",
    tag="pgsql",
    parallel=True,
)
def pg_buffer_cache_hit_ratio_parser(output: str) -> dict:
    df = pd.read_csv(StringIO(output))
    if not df.empty:
        return dict(zip(df.columns, df.iloc[0]))
    else:
        return {}
