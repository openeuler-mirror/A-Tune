#!/bin/bash
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-10-29

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
out_log=/run/atune/${workload}-${tag}

sh $DIR/collect/collect_raw_data.sh ${workload} ${sample_time} ${interval} ${out_log}

echo "start generate training data"
python3 $DIR/parse/parse_data.py ${out_log} ${out} -b ${block_dev} -n ${net_dev} -w ${workload_type} -i ${interval}
