#!/bin/sh
# Copyright (c) 2021 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2021-01-04

path=$(
  cd "$(dirname "$0")"
  pwd
)

echo "update the openGauss yaml"
gausspath=$(ps -ef | grep gaussdb | grep -v grep | awk '{ $1=NULL; print $10 }')
sed -i "s#cat .*/postgresql.conf#cat $gausspath/postgresql.conf#g" "$path"/openGauss_server.yaml
sed -i "s#g' .*/postgresql.conf#g' $gausspath/postgresql.conf#g" "$path"/openGauss_server.yaml

echo "copy the server yaml file to /etc/atuned/tuning/"
cp "$path"/openGauss_server.yaml /etc/atuned/tuning/

benchmark=$(find / -name props.opengauss.1000w)
benchmark_path=${benchmark%/*}
sed -i "s#sh .*/runBenchmark.sh#sh $benchmark_path/runBenchmark.sh#g" "$path"/openGauss_benchmark.sh
sed -i "s#sh .*/openGauss_benchmark.sh#sh $path/openGauss_benchmark.sh#g" "$path"/openGauss_client.yaml
