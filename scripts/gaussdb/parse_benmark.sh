cd /data2/zjh/gitcode/TPCH_tools/tpch_test_logs/latest_logs/
awk -F',' 'NR>1 {sum += $6} END {printf "%.2f\n", sum}' output_off.csv