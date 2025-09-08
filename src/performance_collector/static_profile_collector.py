import logging
import re

from src.utils.shell_execute import cmd_pipeline

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@cmd_pipeline(cmd="lscpu", tag="static", parallel=True)
def lscpu_parser(output: str) -> dict:
    """解析 lscpu 输出：物理/逻辑核心、主频、L3 Cache、NUMA 拓扑"""
    metrics = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        k, v = [x.strip() for x in line.split(":", 1)]
        if k == "CPU(s)":
            metrics["CPU 逻辑核心数量"] = int(v)
        elif k == "Core(s) per socket":
            metrics["每个物理 CPU 插槽上的核心数"] = int(v)
        elif k == "Socket(s)":
            metrics["物理 CPU 插槽数量"] = int(v)
        elif k == "CPU MHz":
            metrics["cpu_mhz"] = float(v)
        elif k == "L3 cache":
            # 格式示例："8192K", "32 MiB (1 instance)"
            m = re.match(r"(\d+)\s*([KMG]i?B?)", v, re.IGNORECASE)
            if m:
                num = int(m.group(1))
                unit = m.group(2).upper()
                if unit in ("K", "KB", "KI", "KIB"):
                    bytes_val = num * 1024
                elif unit in ("M", "MB", "MI", "MIB"):
                    bytes_val = num * 1024**2
                elif unit in ("G", "GB", "GI", "GIB"):
                    bytes_val = num * 1024**3
                else:
                    bytes_val = num
                metrics["L3 缓存容量（字节）"] = bytes_val
        elif k == "NUMA node(s)":
            metrics["NUMA 节点数量"] = int(v)
        elif k.startswith("NUMA node") and "CPU(s)" in k:
            key_name = k.lower().replace(" ", "_")
            metrics[key_name] = v
    return metrics


@cmd_pipeline(cmd="free -b", tag="static", parallel=True)
def free_parser(output: str) -> dict:
    """解析 `free -b` 输出，并将内存大小转换为 GB"""
    metrics = {}

    parts = output.split()
    if len(parts) >= 2 and parts[0].startswith("Mem"):
        total_bytes = int(parts[1])
        total_gb = total_bytes / (1024**3)
        metrics["总共内存大小（GB）"] = round(total_gb, 2)  # 保留 2 位小数
    return metrics


@cmd_pipeline(
    cmd="getconf PAGE_SIZE && grep HugePages_ /proc/meminfo",
    tag="static",
    parallel=True,
)
def page_hugepages_parser(output: str) -> dict:
    """解析 getconf PAGE_SIZE && grep HugePages_ /proc/meminfo，并返回中文键名"""
    metrics = {}
    lines = output.splitlines()
    if lines:
        metrics["系统页大小（字节）"] = int(lines[0].strip())

    field_map = {
        "Total": "HugePages 总数",
        "Free": "HugePages 空闲数",
        "Rsvd": "HugePages 保留但未使用数",
        "Surp": "HugePages 超量分配数",
    }

    for line in lines[1:]:
        m = re.match(r"HugePages_(\w+):\s+(\d+)", line)
        if m:
            key_en = m.group(1)
            key_cn = field_map.get(key_en, f"HugePages_{key_en}")
            metrics[key_cn] = int(m.group(2))

    return metrics


@cmd_pipeline(cmd="lsblk -dn -o NAME,ROTA,TYPE", tag="static", parallel=True)
def lsblk_parser(output: str) -> dict:
    """
    解析 `lsblk -dn -o NAME,ROTA,TYPE` 输出，返回中文键名的磁盘类型信息：
     - ROTA=1 表示旋转盘（HDD），0 表示固态盘（SSD/NVMe）
     - TYPE=d 表示磁盘设备
    """
    metrics = {}
    for line in output.splitlines():
        name, rota, typ = line.split()
        if typ != "d":
            continue
        t = "机械硬盘（HDD）" if rota == "1" else "固态硬盘（SSD/NVMe）"
        metrics[f"磁盘 {name} 类型"] = t
    return metrics


@cmd_pipeline(cmd="iostat -dx -k 1 2", tag="static", parallel=True)
def iostat_parser(output: str) -> dict:
    """
    解析 iostat -dx -k 1 2，取第二次监测
    指标：单盘 IOPS, 顺/随机 吞吐（KB/s）
    """
    metrics = {}
    lines = [
        l
        for l in output.splitlines()
        if l and not l.startswith("Linux") and not l.startswith("avg-cpu")
    ]
    # 找到最后一次 block 设备报告开始行
    # 格式: Device:   rrqm/s wrqm/s r/s w/s ...
    header_idx = None
    for i, l in enumerate(lines):
        if l.startswith("Device"):
            header_idx = i
    if header_idx is None:
        return metrics
    hdr = re.split(r"\s+", lines[header_idx].strip())
    for l in lines[header_idx + 1 :]:
        cols = re.split(r"\s+", l.strip())
        if len(cols) != len(hdr):
            continue
        dev = cols[0]
        data = dict(zip(hdr, cols))
        # IOPS
        metrics[f"{dev}_iops"] = float(data.get("r/s", 0)) + float(data.get("w/s", 0))
        # 吞吐
        metrics[f"{dev}_读操作吞吐率_kB_s"] = float(data.get("rkB/s", 0))
        metrics[f"{dev}_写操作吞吐率_kB_s"] = float(data.get("wkB/s", 0))
    return metrics


@cmd_pipeline(
    cmd='for d in /sys/block/*/queue/nr_requests; do echo "$d $(cat $d)"; done',
    tag="static",
    parallel=True,
)
def queue_depth_parser(output: str) -> dict:
    """解析 /sys/block/*/queue/nr_requests"""
    metrics = {}
    for line in output.splitlines():
        path, val = line.split()
        dev = path.split("/")[3]
        metrics[f"块设备{dev}_队列请求深度"] = int(val)
    return metrics


@cmd_pipeline(cmd="cat /proc/mdstat", tag="static", parallel=True)
def raid_parser(output: str) -> dict:
    """解析 /proc/mdstat：判断是否存在 md 设备及其 RAID 类型（中文键名）"""
    metrics = {}
    for line in output.splitlines():
        if line.startswith("md"):
            parts = line.split()
            name = parts[0]
            # 例如：md0 : active raid1 sda1[0] sdb1[1]
            if "raid" in line:
                m = re.search(r"raid(\d+)", line)
                if m:
                    metrics[f"阵列设备 {name} 类型"] = f"RAID{m.group(1)}"
    return metrics


@cmd_pipeline(cmd="df -T -x tmpfs -x devtmpfs", tag="static", parallel=True)
def df_parser(output: str) -> dict:
    """
    解析 df -T -x tmpfs -x devtmpfs
    返回每个挂载点的文件系统类型
    """
    metrics = {}
    lines = output.strip().splitlines()
    if len(lines) < 2:
        return metrics
    header = re.split(r"\s+", lines[0].strip())
    if "Type" and "Mounted" in header:

        idx_fs = header.index("Type")
        idx_mount = header.index("Mounted")
    elif "类型" and "挂载点" in header:
        idx_fs = header.index("类型")
        idx_mount = header.index("挂载点")
    else:
        return metrics
    for l in lines[1:]:
        cols = re.split(r"\s+", l.strip())
        fs = cols[idx_fs]
        mnt = cols[idx_mount]
        metrics[f"fs_{mnt}"] = fs
    return metrics


@cmd_pipeline(
    cmd="ethtool $(ls /sys/class/net | grep -v lo | head -n1)",
    tag="static",
    parallel=True,
)
def nic_queues_parser(output: str) -> dict:
    """
    解析 ethtool -l 输出：NIC 多队列信息
    """
    metrics = {}
    for line in output.splitlines():
        if "Combined:" in line:
            _, val = line.split(":", 1)
            metrics["nic_combined_queues"] = int(val.strip())
    return metrics


@cmd_pipeline(
    cmd="ethtool -l $(ls /sys/class/net | grep -v lo | head -n1)",
    tag="static",
    parallel=True,
)
def ethtool_speed_parser(output: str) -> dict:
    """
    解析 ethtool 输出：网络带宽（Speed）
    """
    metrics = {}
    m = re.search(r"Speed:\s*(\d+)([GM]b/s)", output)
    if m:
        metrics["网络速度"] = m.group(1) + m.group(2)
    return metrics


@cmd_pipeline(cmd="lspci -vv | grep -i sriov -A5", tag="static", parallel=True)
def sriov_parser(output: str) -> dict:
    """
    解析 lspci -vv | grep -i sriov -A5：是否支持 SR-IOV，最大 VF 数
    """
    metrics = {}
    for line in output.splitlines():
        if "SR-IOV" in line and "Total VFs:" in line:
            m = re.search(r"Total VFs:\s*(\d+)", line)
            if m:
                metrics["nic_sriov_total_vfs"] = int(m.group(1))
    return metrics


@cmd_pipeline(cmd="ulimit -n", tag="static", parallel=True)
def fdlimit_parser(output: str) -> dict:
    """解析 ulimit -n 输出：文件描述符上限"""
    return {"最大文件描述符": int(output.strip())}
