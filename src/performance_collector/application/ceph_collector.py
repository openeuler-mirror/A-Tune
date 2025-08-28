import json
import re

from src.utils.collector.metric_collector import (
    snapshot_task,
    CollectMode,
)


@snapshot_task(
    cmd="ceph -s",
    collect_mode=CollectMode.ASYNC,
    tag="ceph集群状态信息",
)
def parse_ceph_s(output: str) -> dict:
    result = {}

    # degraded objects
    degraded_match = re.search(r"(\d+)\s+degraded objects", output)
    if degraded_match:
        result["降级对象数"] = int(degraded_match.group(1))

    # recovery speed
    recovery_match = re.search(r"recovery io.*?([\d\.]+)\s*([KMGT]?B)/s", output)
    if recovery_match:
        result["恢复速度"] = recovery_match.group(1) + recovery_match.group(2)

    # slow ops
    slow_ops_match = re.search(r"(\d+)\s+slow ops", output)
    if slow_ops_match:
        result["慢请求数"] = int(slow_ops_match.group(1))

    return {"ceph -s": result}


@snapshot_task(
    cmd="ceph df",
    collect_mode=CollectMode.ASYNC,
    tag="ceph磁盘使用情况",
)
def parse_ceph_df_output(text: str) -> dict:
    result = {
        "总容量": None,
        "已用容量": None,
        "可用容量": None,
        "使用率(%)": None,
        "存储类型": [],
        "存储池": []
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
                "类型": parts[0],
                "总容量": parts[1],
                "可用容量": parts[2],
                "已用容量": parts[3],
                "原始已用容量": parts[4],
                "原始使用率(%)": float(parts[5])
            }
            result["存储类型"].append(storage)

            if parts[0] == "TOTAL":
                result["总容量"] = parts[1]
                result["可用容量"] = parts[2]
                result["已用容量"] = parts[3]
                result["使用率(%)"] = float(parts[5])

        elif section == 'pools' and len(parts) >= 7:
            pool = {
                "名称": parts[0],
                "ID": int(parts[1]),
                "PG数量": int(parts[2]),
                "存储量": parts[3],
                "对象数": int(parts[4]),
                "已用容量": parts[5],
                "使用率(%)": float(parts[6]),
                "最大可用容量": parts[7] if len(parts) > 7 else None
            }
            result["存储池"].append(pool)

    return {"ceph df": result}


@snapshot_task(
    cmd="ceph pg stat",
    collect_mode=CollectMode.ASYNC,
    tag="ceph PG（Placement Groups，数据放置组）的详细状态统计",
)
def parse_ceph_pg_stat(output: str) -> dict:
    result = {}
    pg_match = re.search(r"(\d+)\s+active.+", output)
    if pg_match:
        result["PG 总数"] = int(pg_match.group(1))
    return {"ceph pg stat": result}


@snapshot_task(
    cmd="ceph tell osd.* perf dump",
    collect_mode=CollectMode.ASYNC,
    tag="所有 OSD 的性能统计数据，包含操作延迟、IOPS、吞吐等指标",
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
        "osd.op_r": "读请求数",
        "osd.op_w": "写请求数",
        "osd.op_latency.avgcount": "总体请求数",
        "osd.op_latency.avgtime": "平均请求延迟(s)",
        "osd.op_r.avgtime": "平均读延迟(s)",
        "osd.op_w.avgtime": "平均写延迟(s)",
        "bluefs.db_write_bytes": "BlueFS写入字节数",
        "bluefs.wal_write_bytes": "BlueFS WAL写入字节数",
        "filestore.journal_latency.avgcount": "Journal请求数",
        "filestore.journal_latency.avgtime": "Journal延迟平均(s)",
        "bluestore.kv_commit_lat.avgtime": "KV提交延迟(s)"
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
