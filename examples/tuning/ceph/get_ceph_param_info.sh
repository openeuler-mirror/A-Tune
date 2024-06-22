#!/bin/bash

# 检查参数个数
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <metric_name>"
    exit 1
fi

# 读取参数
METRIX_NAME=$1

# 获取 OSD 节点信息的第一个节点名称
NODE_NAME=$(ceph node ls | jq -r '.osd | keys[0]')

# 检查是否成功获取到节点名称
if [ -z "$NODE_NAME" ]; then
    echo "Failed to get the first node name."
    exit 1
fi

# 假设第一个节点的 OSD ID 列表中的第一个 OSD ID
OSD_ID=$(ceph node ls | jq -r ".osd[\"$NODE_NAME\"][0]")

# 检查是否成功获取到 OSD ID
if [ -z "$OSD_ID" ]; then
    echo "Failed to get the first OSD ID for node $NODE_NAME."
    exit 1
fi

# 执行 SSH 命令获取配置值
VALUE=$(ssh -q "${NODE_NAME}" "ceph daemon osd.${OSD_ID} config get ${METRIX_NAME}" | jq -r '. | values | .[]')

# 检查 SSH 命令是否执行成功
echo ${VALUE}
