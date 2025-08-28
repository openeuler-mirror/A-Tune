#!/bin/bash

LOG_FILE=/home/wsy/benchmark.log

convert_to_k() {
  val=$1
  unit=$2
  case "$unit" in
    K/s) echo "$val" ;;
    M/s) awk -v v="$val" 'BEGIN{printf "%.3f", v*1000}' ;;
    *) echo 0 ;;
  esac
}

total_throughput=$(grep '|Total' "$LOG_FILE" | awk -F'|' '
  {
    # ~O~V~@~R~U__~L~H~W~L~N__|
    gsub(/^ +| +$/, "", $(NF-1))
    split($(NF-1), a, " ")
    val = a[1]
    unit = a[2]
    if (unit == "M/s") val *= 1000
    total += val
  }
  END {printf "%.3f\n", total}
')

echo "$total_throughput"

timestamp=$(date +"%Y%m%d-%H%M%S")

mkdir -p /home/wsy/logs

mv /home/wsy/benchmark.log "/home/wsy/logs/${timestamp}-benchmark.log"
