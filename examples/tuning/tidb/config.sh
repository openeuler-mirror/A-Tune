#!/bin/sh
# Copyright (c) liyang(innovation64feng@gmail.com),
# Information Management and Information System, Beijing University of Chinese Medicine.
#
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
#
# Create: 2021-09-30

#输入服务器脚本位置
# 输入服务器IP
DB_HOST=$1
CONFIG_PATH=$2



sed -i "s|^CONFIG_PATH=*|CONFIG_PATH=${CONFIG_PATH}|g" tidb.sh
sed -i "s/^DB_HOST=.*/DB_HOST=${DB_HOST}/g" auto_run.sh
sed -i "s|^SCRIPT_PATH=.*|SCRIPT_PATH=${CONFIG_PATH}|g" auto_run.sh
scp prepare_data.sh root@$DB_HOST:$CONFIG_PATH
scp start_tidb.sh root@$DB_HOST:$CONFIG_PATH
scp install-tidb.sh root@$DB_HOST:$CONFIG_PATH
scp topo.yaml root@$DB_HOST:$CONFIG_PATH
scp install-sysbench.sh root@$DB_HOST:$CONFIG_PATH