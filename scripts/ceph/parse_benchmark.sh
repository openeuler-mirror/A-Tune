#!/bin/bash
SCRIPT_PATH="$(realpath "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
cd "$SCRIPT_DIR"
sh benchmark.sh > benchmark.log 2>&1
grep "bandwidth_val" benchmark.log | awk '{print $3}'

