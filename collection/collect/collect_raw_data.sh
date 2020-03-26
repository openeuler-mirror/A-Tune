#!/bin/bash
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-10-29

if [ ! $# == 4 ]; then
	echo "Usage: collect_raw_data.sh workload sample_time sample_interval out_log"
	exit
fi

DIR=$(dirname $0)

bench=$1
sample_time=$2
interval=$3
out_log=$4
tag=$(date +%Y%m%d-%H%M%S)

pids=$(pidof mpstat)
for pid in $pids
do
	kill -15 $pid
done
pids=$(pidof vmstat)
for pid in $pids
do
	kill -15 $pid
done
pids=$(pidof iostat)
for pid in $pids
do
	kill -15 $pid
done
pids=$(pidof perf)
for pid in $pids
do
	kill -15 $pid
done
pids=$(pidof sar)
for pid in $pids
do
	kill -15 $pid
done

killall get_meminfo.sh 2>/dev/null
killall get_sysctl.sh 2>/dev/null

mkdir -p $out_log

#echo 3 > /proc/sys/vm/drop_caches
echo "start collect raw data"

LC_TIME="POSIX" mpstat -P ALL ${interval} > ${out_log}/${bench}-mpstat-${tag}.log &
LC_TIME="POSIX" sar -w ${interval} > ${out_log}/${bench}-sar-task-${tag}.log &
LC_TIME="POSIX" sar -q ${interval} > ${out_log}/${bench}-sar-load-${tag}.log &
LC_TIME="POSIX" sar -B ${interval} > ${out_log}/${bench}-sar-paging-${tag}.log &
LC_TIME="POSIX" sar -n EDEV ${interval} > ${out_log}/${bench}-sar-net_err-${tag}.log &
LC_TIME="POSIX" sar -n DEV ${interval} > ${out_log}/${bench}-sar-network-${tag}.log &
vmstat -n ${interval} > ${out_log}/${bench}-vmstat-${tag}.log &
iostat -x -m -d ${interval} > ${out_log}/${bench}-iostat-${tag}.log &
stdbuf -oL sh $DIR/perf-cpu.sh ${interval} > ${out_log}/${bench}-perf-cpu-${tag}.log &
stdbuf -oL sh $DIR/perf-memBW.sh ${interval} > ${out_log}/${bench}-perf-memBW-${tag}.log &
$DIR/get_meminfo.sh ${interval} > ${out_log}/${bench}-meminfo-${tag}.log &
$DIR/get_sysctl.sh ${interval} > ${out_log}/${bench}-sysctl-${tag}.log &


#collection time
sleep ${sample_time}


pids=$(pidof mpstat)
for pid in $pids
do
	kill -15 $pid
done
pids=$(pidof vmstat)
for pid in $pids
do
	kill -15 $pid
done
pids=$(pidof iostat)
for pid in $pids
do
	kill -15 $pid
done
pids=$(pidof perf)
for pid in $pids
do
	kill -15 $pid
done
pids=$(pidof sar)
for pid in $pids
do
	kill -15 $pid
done

killall get_meminfo.sh
killall get_sysctl.sh
