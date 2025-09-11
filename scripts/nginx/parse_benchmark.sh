#!/bin/bash

SCRIPT_PATH="$(realpath "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
cd "$SCRIPT_DIR"

# 运行benchmark.sh，传入所有参数，输出重定向到benchmark.log
sh benchmark.sh $1 $2 > benchmark.log 2>&1

# 从benchmark.log中提取 rps（Requests per second）
# 以 httpress 输出的 TIMING 行为例，第四个字段是 rps
grep 'TIMING:' benchmark.log | awk '{print $4}'