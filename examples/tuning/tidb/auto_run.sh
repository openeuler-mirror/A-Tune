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
MYSQL_BIN=/usr/local/mysql/bin/mysql
SCRIPT_PATH= 
DB_HOST=
TESTS="oltp_point_select"
TABLE_SIZE=100000

sed -i "s/^mysql-host=.*/mysql-host=${DB_HOST}/g" config


unset http_proxy
unset https_proxy
mkdir -p result

for test in $TESTS
do 
    ssh root@$DB_HOST "source ~/.bash_profile; cd $SCRIPT_PATH; sh prepare_data.sh $DB_HOST $TABLE_SIZE $test  /dev/null  /tmp/prepare.log 2>$1"
    sleep 20
    echo "Start to run $test, $TABLE_SIZE"
    while true
    do 
        sysbench --config-file=config $test --tables=32 --table-size=$TABLE_SIZE --time=300 --mysql-ignore-errors=8005 run 2>&1 > result/$test.log
        rst='cat result/$test.log | grep "queries performed:" | grep -v grep'
        if [[ $? -eq 0 ]] ;  then
            break 
        fi
        sleep 10
    done
    cp result/$test.log result/last.log
done 
