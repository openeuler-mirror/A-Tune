#!/bin/sh
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
#
# A-Tune is licensed under the Mulan PSL v1.
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
# Create: 2020-01-09
# Author: zhangtaibo <sonice1755@163.com>

export TCID="atune-adm list cmd test"

. ./test_lib.sh

init()
{
    echo "init the sysytem"
    check_service_started atuned
}

cleanup()
{
    echo "===================="
    echo "Clean the System"
    echo "===================="
    rm -rf temp.log
}

test01()
{
    tst_resm TINFO "atune-adm list cmd test"
    # Check all supported workload were listed
    atune-adm list > temp.log
    for ((i=0;i<${#ARRAY_WORKLOADTYPE[@]};i++));do
        grep "${ARRAY_WORKLOADTYPE[i]}" temp.log
        check_result $? 0
    done

    # Help info
    atune-adm list -h > temp.log
    grep "list current support workload type" temp.log
    check_result $? 0

    # Extra input
    atune-adm list extra_input > temp.log
    grep "Incorrect Usage." temp.log
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
