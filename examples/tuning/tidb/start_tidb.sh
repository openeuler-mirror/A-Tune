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

PD_DIR=/home/huangduirong/pd
TIKV_DIR=/home/huangduirong/tikv
TIDB_DIR=/home/huangduirong/tidb
DATA_PATH=/home/tidb_data
CONFIG_PATH=/home/huangduirong/tidb_tunning
IP_CONFIG=9.82.177.199

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
    --log-file=$DATA_PATH/pd1.log &
sleep 5
$TIKV_DIR/target/release/tikv-server --pd-endpoints="$IP_CONFIG:2379" \
    --addr="$IP_CONFIG:20160" \
    --status-addr="$IP_CONFIG:20181" \
    --config=$CONFIG_PATH/tikv_config.toml \
    --data-dir=$DATA_PATH/tikv1 \
    --log-file=$DATA_PATH/tikv1.log &
$TIKV_DIR/target/release/tikv-server --pd-endpoints="$IP_CONFIG:2379" \
    --addr="$IP_CONFIG:20161" \
    --status-addr="$IP_CONFIG:20182" \
    --config=$CONFIG_PATH/tikv_config.toml \
    --data-dir=$DATA_PATH/tikv2 \
    --log-file=$DATA_PATH/tikv2.log &
$TIKV_DIR/target/release/tikv-server --pd-endpoints="$IP_CONFIG:2379" \
    --addr="$IP_CONFIG:20162" \
    --status-addr="$IP_CONFIG:20183" \
    --config=$CONFIG_PATH/tikv_config.toml \
    --data-dir=$DATA_PATH/tikv3 \
    --log-file=$DATA_PATH/tikv3.log &
sleep 5
$TIDB_DIR/bin/tidb-server --store=tikv \
    --path="$IP_CONFIG:2379" \
    --log-file=$DATA_PATH/tidb.log \
    -L=error \
    --config=tidb_config.toml &
sleep 5
