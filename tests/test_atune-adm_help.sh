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

export TCID="atune-adm help cmd test"

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
    tst_resm TINFO "atune-adm help cmd test"
    array=("help" "--help" "-h" "")
    for ((i=0;i<${#array[@]};i++));do
        atune-adm ${array[i]} > temp.log
        check_result $? 0

        grep "atune-adm - atune-adm is a command line client for atuned AI tuning system" temp.log
        check_result $? 0
    done

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
