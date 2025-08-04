#!/bin/bash

# 参数设置
REDIS_HOST="${1:-127.0.0.1}"
REDIS_PORT="${2:-6379}"

echo 1 > /tmp/euler-copilot-fifo

# 运行 redis-benchmark 并保存输出
redis-benchmark -h "$REDIS_HOST" -p "$REDIS_PORT" -t set,get,incr,rpop,sadd,hset,lrange_600 --csv 

echo $OUTPUT > benchmark.log

# 解析 CSV 输出并计算总 QPS
TOTAL_QPS=$(echo "$OUTPUT" | awk -F',' '{gsub(/"/,""); sum += $2} END {printf "%.2f", sum}')

echo "$TOTAL_QPS"
