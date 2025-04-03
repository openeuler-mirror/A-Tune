#!/bin/bash

# 在远程服务器上执行脚本并放入后台
ssh -q root@CLIENT_IP_2 "cd PATH && rm -rf tpcc_benchmark.log && sh tpcc_benchmark.sh > tpcc_benchmark.log 2>&1 &"

sleep 5

# 监控远程日志，检测到特定日志内容时终止
while ! ssh -q root@CLIENT_IP_2 '[ -f PATH/tpcc/mariadb_tpmc.out ]'; do sleep 2; done && ssh -q root@CLIENT_IP_2 'kill $(pgrep -f tpcc_benchmark.sh)'

# 等待所有后台进程完成
wait
