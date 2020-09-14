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
# Create: 2020-01-09
# Author: zhangtaibo <sonice1755@163.com>

export TCID="atune-adm check cmd test"

. ./test_lib.sh

init()
{
    echo "init the system"
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
    tst_resm TINFO "atune-adm check cmd test"
    # Check cmd function
    atune-adm check > temp.log
    check_result $? 0

    grep -i "Check finished" temp.log
    check_result $? 0

    # Help info
    atune-adm check -h > temp.log
    grep "check system basic information" temp.log
    check_result $? 0

    # Extra input
    atune-adm check extra_input > temp.log
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
