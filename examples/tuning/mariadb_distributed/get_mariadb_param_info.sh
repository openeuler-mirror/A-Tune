#!/bin/bash
set -x

# 检查是否传入参数
if [ -z "$1" ]; then
  echo "请提供一个参数"
  exit 1
fi

# 获取传入的参数
param=$1


mysql -h SERVER_IP_1 -u root -e "SHOW VARIABLES LIKE '$1';" | grep -i "$1" | awk '{print $2}'