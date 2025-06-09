#!/bin/bash
SCRIPT_PATH="$(realpath "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
cd "$SCRIPT_DIR"
ssh root@9.82.36.53  "cd /home/cxm"
cd /home/cxm
time_taken=$(grep "time_taken:" "spark_benchmark.log" \
| sed -nE 's/.*time_taken:([0-9.]+)s.*/\1/p' \
| grep -E '^[0-9.]+' \
| paste -sd+ \
| bc \
| xargs printf "%.2f")

echo $time_taken