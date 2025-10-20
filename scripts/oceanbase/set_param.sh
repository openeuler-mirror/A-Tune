#!/bin/bash
# 需要把该脚本移动至oceanbase应用部署机器上

param_name=$1
param_value=$2
config_file="/root/.obd/cluster/obcluster/config.yaml"

# 如果参数已存在，只修改第一次出现的地方
if grep -q "^[[:space:]]*$param_name:" "$config_file"; then
  sed -i "0,/^[[:space:]]*$param_name:.*/s//  $param_name: $param_value/" "$config_file"
else
  # 如果不存在，在第一个 global: 后插入
  awk -v key="$param_name" -v val="$param_value" '
    BEGIN {inserted=0}
    /^  global:/ {
      print
      if (!inserted) {
        print "    " key ": " val
        inserted=1
      }
      next
    }
    {print}
  ' "$config_file" > /tmp/tmp_conf && mv /tmp/tmp_conf "$config_file"
fi