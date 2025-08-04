#!/bin/bash
SCRIPT_PATH="$(realpath "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
cd "$SCRIPT_DIR"
sh benchmark.sh $1 $2 > benchmark.log 2>&1
cat benchmark.log | awk -F',' '{gsub(/"/,""); sum += $2} END {printf "%.2f", sum}'