#!/bin/sh
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
#
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2020-01-06
# Author: zhangtaibo <sonice1755@163.com>

export TCID="atuned.cnf Disk configuration test"

. ./test_lib.sh

init()
{
    echo "init the system"
    cp -a  $ATUNE_CONF $ATUNE_CONF.bak
}

cleanup()
{
    echo "===================="
    echo "Clean the System"
    echo "===================="
    mv $ATUNE_CONF.bak $ATUNE_CONF
    rm -rf $ANALYSIS_LOG
}

test01()
{
    tst_resm TINFO "atuned.cnf file's disk configuration test"
    # Reduce the numbers of collected data, reduce testcase running time
    change_conf_value sample_num 2

    # Correct configuration test
    sys_disk=`lsscsi | awk '($NF~/dev/){print $NF}' | awk -F '/' '{print $NF}' | awk 'NR==1{print $1}'`
    change_conf_value disk $sys_disk
    systemctl restart $ATUNE_SERVICE_NAME
    wait_service_ready $ATUNE_SERVICE_NAME
    atune-adm analysis
    check_result $? 0

    # The value of the disk configuration is special character and ultra long character and null
    array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "")
    for ((i=0;i<${#array[@]};i++));do
        change_conf_value disk ${array[i]}
        systemctl restart $ATUNE_SERVICE_NAME
        wait_service_ready $ATUNE_SERVICE_NAME
        atune-adm analysis > $ANALYSIS_LOG
        check_result $? 1
        
        grep "collect data failed" $ANALYSIS_LOG
        check_result $? 0
    done
    
    # Comment disk configuration
    comment_conf_value disk
    systemctl restart $ATUNE_SERVICE_NAME
    wait_service_ready $ATUNE_SERVICE_NAME
    atune-adm analysis
    check_result $? 1

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi

}

TST_CLEANUP=cleanup

init

test01

tst_exit

