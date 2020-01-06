#!/bin/sh
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
#
# The implementation was written so as to confirm atuned services.
#
# A-Tune is licensed under the Mulan PSL v1.
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
# Create: 2020-01-06
# Author: zhangtaibo <sonice1755@163.com>

export TCID="atuned.cnf configuration test"

. ./test_lib.sh

init()
{
    echo "init the sysytem"
    rpminstall net-tools
    cp -a  $ATUNE_CONF $ATUNE_CONF.bak
    # Reduce the numbers of collected data, reduce testcase running time
    change_conf_value sample_num 2
    systemctl restart $ATUNE_SERVICE_NAME
    wait_service_ready $ATUNE_SERVICE_NAME
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
    tst_resm TINFO "atuned.cnf file's port configuration test"
    netstat -anp | grep 60001 | grep atuned
    check_result $? 0
    
    atune-adm analysis
    check_result $? 0

    atune-adm analysis
    check_result $? 0

    change_conf_value port ""
    systemctl restart $ATUNE_SERVICE_NAME
    wait_service_ready $ATUNE_SERVICE_NAME
    netstat -anp | grep 60001 | grep atuned
    check_result $? 0

    atune-adm analysis
    check_result $? 0


    array=("$SPECIAL_CHARACTERS" "65536" "-1")
    for ((i=0;i<${#array[@]};i++));do
        change_conf_value port ${array[i]}
        systemctl restart $ATUNE_SERVICE_NAME
        check_result $? 1
    done

    comment_conf_value port
    systemctl restart $ATUNE_SERVICE_NAME
    wait_service_ready $ATUNE_SERVICE_NAME
    netstat -anp | grep 60001 | grep atuned
    check_result $? 0

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

