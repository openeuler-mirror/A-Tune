#!/bin/sh
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
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

echo "update the openGauss"
ps -ef | grep gauss > openGuass.txt
cat openGuass.txt | grep gaussdb | awk '{ $1=NULL; print $10 }'
gausspath=$(cat openGuass.txt | grep gaussdb | awk '{ $1=NULL; print $10 }')
sed -i "s#cat .*/postgresql.conf#cat $gausspath/postgresql.conf#g" /etc/atuned/tuning/openGauss.yaml
sed -i "s#g' .*/postgresql.conf#g' $gausspath/postgresql.conf#g" /etc/atuned/tuning/openGauss.yaml


echo "update the tpcc client"
sed -i "s#sh .*/openGauss_run.sh#sh $path/openGauss_run.sh#g" $path/openGauss-client.yaml
sed -i "s#sh .*/collect_openGauss.sh#sh $path/collect_openGauss.sh#g" $path/openGauss-client.yaml
rm -rf openGuass.txt

