#!/bin/bash

if [ ! $# == 7 ]; then
	echo "Usage: collect_training_data.sh workload sample_time sample_interval out block_dev net_dev workload_type"
	exit
fi


workload=$1
sample_time=$2
interval=$3
out=$4
block_dev=$5
net_dev=$6
workload_type=$7
tag=$(date +%Y%m%d-%H%M%S)

DIR=$(dirname $0)
out_log=/tmp/atune/${workload}-${tag}

sh $DIR/collect_raw_data.sh ${workload} ${sample_time} ${interval} ${out_log} 

echo "start generate training data"
python3 $DIR/parse_data.py ${out_log} ${out} -b ${block_dev} -n ${net_dev} -w ${workload_type}
