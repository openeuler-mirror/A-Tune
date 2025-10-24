#!/bin/bash
SCRIPT_PATH="$(realpath "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
cd "$SCRIPT_DIR"
sh benchmark.sh > benchmark.log 2>&1
grep "queries:" benchmark.log | awk -F'[()]' '{print $2}' | awk '{print $1}'