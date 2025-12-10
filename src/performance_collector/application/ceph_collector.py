import json
import re
from src.utils.common import translate

from src.utils.collector.metric_collector import (
    snapshot_task,
    CollectMode,
)


@snapshot_task(
    cmd="ceph -s",
    collect_mode=CollectMode.ASYNC,
    tag=translate("ceph集群状态信息", "Ceph cluster status information"),
)
def parse_ceph_s(output: str) -> dict:
    result = {}

    # degraded objects
    degraded_match = re.search(r"(\d+)\s+degraded objects", output)
    if degraded_match:
        result["degraded_object_count"] = int(degraded_match.group(1))

    # recovery speed
    recovery_match = re.search(r"recovery io.*?([\d\.]+)\s*([KMGT]?B)/s", output)
    if recovery_match:
        result["recovery_speed"] = recovery_match.group(1) + recovery_match.group(2)

    # slow ops
    slow_ops_match = re.search(r"(\d+)\s+slow ops", output)
    if slow_ops_match:
        result["slow_request_count"] = int(slow_ops_match.group(1))

    return {"ceph -s": result}


@snapshot_task(
    cmd="ceph df",
    collect_mode=CollectMode.ASYNC,
    tag=translate("ceph磁盘使用情况", "Ceph disk usage"),
)
def parse_ceph_df_output(text: str) -> dict:
    result = {
        "total_capacity": None,
        "used_capacity": None,
        "available_capacity": None,
        "utilization(%)": None,
        "storage_type": [],
        "storage_pool": []
    }

    lines = text.strip().splitlines()
    section = None

    for line in lines:
        line = line.strip()
        if line.startswith('--- RAW STORAGE'):
            section = 'raw'
            continue
        elif line.startswith('--- POOLS'):
            section = 'pools'
            continue
        elif not line or line.startswith('CLASS') or line.startswith('POOL'):
            continue

        parts = re.split(r'\s{2,}|\t', line)

        if section == 'raw' and len(parts) >= 6:
            storage = {
                "type": parts[0],
                "total_capacity": parts[1],
                "available_capacity": parts[2],
                "used_capacity": parts[3],
                "raw_used_capacity": parts[4],
                "raw_utilization(%)": float(parts[5])
            }
            result["storage_type"].append(storage)

            if parts[0] == "TOTAL":
                result["total_capacity"] = parts[1]
                result["available_capacity"] = parts[2]
                result["used_capacity"] = parts[3]
                result["utilization(%)"] = float(parts[5])

        elif section == 'pools' and len(parts) >= 7:
            pool = {
                "name": parts[0],
                "id": int(parts[1]),
                "pg_count": int(parts[2]),
                "stored_count": parts[3],
                "objects_count": int(parts[4]),
                "used_capacity": parts[5],
                "utilization(%)": float(parts[6]),
                "max_available_capacity": parts[7] if len(parts) > 7 else None
            }
            result["storage_pool"].append(pool)

    return {"ceph df": result}


@snapshot_task(
    cmd="ceph pg stat",
    collect_mode=CollectMode.ASYNC,
    tag=translate("ceph PG（Placement Groups，数据放置组）的详细状态统计", "Detailed status statistics of Ceph PG (Placement Groups)"),
)
def parse_ceph_pg_stat(output: str) -> dict:
    result = {}
    pg_match = re.search(r"(\d+)\s+active.+", output)
    if pg_match:
        result["pg_count"] = int(pg_match.group(1))
    return {"ceph pg stat": result}


@snapshot_task(
    cmd="ceph tell osd.* perf dump",
    collect_mode=CollectMode.ASYNC,
    tag=translate("所有 OSD 的性能统计数据，包含操作延迟、IOPS、吞吐等指标", "Performance statistics for all OSDs, including metrics such as operation latency, IOPS, throughput, etc."),
)
def parse_perf_dump_str(raw_str: str) -> dict:
    def get_value_by_path(d, path):
        keys = path.split('.')
        cur = d
        for k in keys:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(k)
            if cur is None:
                return None
        return cur

    path_map = {
        "osd.op_r": "read_ops",
        "osd.op_w": "write_ops",
        "osd.op_latency.avgcount": "total_ops",
        "osd.op_latency.avgtime": "avg_request_latency(s)",
        "osd.op_r.avgtime": "avg_read_latency(s)",
        "osd.op_w.avgtime": "avg_write_latency(s)",
        "bluefs.db_write_bytes": "bluefs_db_write_bytes",
        "bluefs.wal_write_bytes": "bluefs_wal_write_bytes",
        "filestore.journal_latency.avgcount": "journal_ops",
        "filestore.journal_latency.avgtime": "avg_journal_latency(s)",
        "bluestore.kv_commit_lat.avgtime": "kv_commit_latency(s)"
    }

    # 解析多osd json字符串
    pattern = re.compile(r'(osd\.\d+):\s*({.*?})(?=(?:\nosd\.\d+:)|\Z)', re.S)
    result = {}

    for match in pattern.finditer(raw_str):
        osd_name = match.group(1)
        json_str = match.group(2)

        try:
            perf_data = json.loads(json_str)
        except json.JSONDecodeError:
            perf_data = {}

        metrics = {}
        for eng_path, cn_name in path_map.items():
            val = get_value_by_path(perf_data, eng_path)
            if val is not None:
                metrics[cn_name] = val

        result[osd_name] = metrics

    return {"ceph tell osd.* perf dump": result}
