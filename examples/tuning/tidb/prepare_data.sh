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

if [ $# -lt 3 ];then
    echo "ERROR: usage: prepare_data.sh {DB_IP} {TABLE_SIZE} {TEST_NAM}"
    exit 1
fi

DB_HOST=$1
TABLE_SIZE=$2
test=$3

MYSQL_BIN=mysql
$MYSQL_BIN  --help 2>&1 > /dev/null
if [ $? -ne 0 ]; then
	if [ -f "/usr/local/mysql/bin/mysql" ]; then
		MYSQL_BIN=/usr/local/mysql/bin/mysql
	elif [ -f "/usr/bin/mysql" ]; then
		MYSQL_BIN=/usr/bin/mysql
	fi
fi

ps -ef | grep pd-server | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep tikv-server | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep tidb-server | grep -v grep | awk '{print $2}' | xargs kill -9

unset http_proxy
unset https_proxy

sed -i "s/^mysql-host=.*/mysql-host=${DB_HOST}/g" config
sed -i "s/^IP_CONFIG=.*/IP_CONFIG=${DB_HOST}/g" start_tidb.sh

sh start_tidb.sh 
sleep 60
$MYSQL_BIN -h $DB_HOST -P 4000 -u root -D sbtest \
-Be "DROP DATABASE sbtest;"

$MYSQL_BIN -h $DB_HOST -P 4000 -u root -Be "create database sbtest;"
# $MYSQL_BIN -h $DB_HOST -P 4000 -u root -D sbtest \
# -Be "SET GLOBAL tidb_disable_txn_auto_retry = 0;"
# $MYSQL_BIN -h $DB_HOST -P 4000 -u root -D sbtest \
# -Be "SET GLOBAL tidb_retry_limit = 10000;"

sysbench --config-file=config $test \
	 --tables=32 --table-size=$TABLE_SIZE --time=30 prepare

