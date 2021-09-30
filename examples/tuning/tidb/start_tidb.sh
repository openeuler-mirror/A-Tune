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
# Create: 2021-06-03

PD_DIR=/tidb-deploy/pd-2379
TIKV_DIR=/tidb-deploy
TIDB_DIR=/tidb-deploy/tidb-4000
DATA_PATH=/tidb-data
IP_CONFIG=

ps -ef | grep pd-server | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep tikv-server | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep tidb-server | grep -v grep | awk '{print $2}' | xargs kill -9

unset http_proxy
unset https_proxy

$PD_DIR/bin/pd-server --name=pd1 \
    --data-dir=$DATA_PATH/pd1 \
    --client-urls="http://$IP_CONFIG:2379" \
    --peer-urls="http://$IP_CONFIG:2380" \
    --initial-cluster="pd1=http://$IP_CONFIG:2380" \
    --log-file=$PD_DIR/log/pd.log &
sleep 5
$TIKV_DIR/tikv-20160/bin/tikv-server --pd-endpoints="$IP_CONFIG:2379" \
    --addr="$IP_CONFIG:20160" \
    --status-addr="$IP_CONFIG:20180" \
    --config=$TIKV_DIR/tikv-20160/conf/tikv.toml \
    --data-dir=$DATA_PATH/tikv1 \
    --log-file=$TIKV_DIR/tikv-20160/log/tikv.log &
$TIKV_DIR/tikv-20161/bin/tikv-server --pd-endpoints="$IP_CONFIG:2379" \
    --addr="$IP_CONFIG:20161" \
    --status-addr="$IP_CONFIG:20181" \
    --config=$TIKV_DIR/tikv-20161/conf/tikv.toml \
    --data-dir=$DATA_PATH/tikv2 \
    --log-file=$TIKV_DIR/tikv-20161/log/tikv.log &
$TIKV_DIR/tikv-20162/bin/tikv-server --pd-endpoints="$IP_CONFIG:2379" \
    --addr="$IP_CONFIG:20162" \
    --status-addr="$IP_CONFIG:20182" \
    --config=$TIKV_DIR/tikv-20162/conf/tikv.toml \
    --data-dir=$DATA_PATH/tikv3 \
    --log-file=$TIKV_DIR/tikv-20162/log/tikv.log &
sleep 5
$TIDB_DIR/bin/tidb-server --store="tikv" \
    --path="$IP_CONFIG:2379" \
    --log-file=$TIDB_DIR/log/tidb.log \
    -L=error \
    --config=$TIDB_DIR/conf/tidb.toml &
sleep 120
