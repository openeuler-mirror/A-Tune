#!/bin/bash
set -x

# 检查是否传入参数
if [ -z "$1" ]; then
  echo "请提供一个参数"
  exit 1
fi

# 获取传入的参数
param=$1
value=$2

# 构建命令
ssh -q root@SERVER_IP_1 "bash -c 'grep -q \"^$param\" /etc/my.cnf && sed -i \"s/^$param.*/$param = $value/g\" /etc/my.cnf || echo \"$param = $value\" >> /etc/my.cnf'"

ssh -q root@SERVER_IP_2 "bash -c 'grep -q \"^$param\" /etc/my.cnf && sed -i \"s/^$param.*/$param = $value/g\" /etc/my.cnf || echo \"$param = $value\" >> /etc/my.cnf'"
