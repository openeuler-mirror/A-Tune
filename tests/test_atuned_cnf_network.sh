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

export TCID="atuned.cnf Network configuration test"

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
}

test01()
{
    tst_resm TINFO "atuned.cnf file's network configuration test"
    # Reduce the numbers of collected data, reduce testcase running time
    change_conf_value sample_num 2

    # Correct configuration test
    sys_network=`ip address | grep UP | awk 'NR==1{print $2}' | awk -F ':' '{print $1}'`
    check_conf_value network $sys_network

    systemctl restart $ATUNE_SERVICE_NAME
    wait_service_ready $ATUNE_SERVICE_NAME
    atune-adm analysis
    check_result $? 0

    # The value of the network configuration is special character and ultra long character and null
    array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "")
    for ((i=0;i<${#array[@]};i++));do
        change_conf_value network ${array[i]}
        systemctl restart $ATUNE_SERVICE_NAME
        wait_service_ready $ATUNE_SERVICE_NAME
        atune-adm analysis
        check_result $? 0
    done
    
    # Comment network configuration
    comment_conf_value network
    systemctl restart $ATUNE_SERVICE_NAME
    wait_service_ready $ATUNE_SERVICE_NAME
    atune-adm analysis
    check_result $? 0

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

