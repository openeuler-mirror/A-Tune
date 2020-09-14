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

export TCID="atune-adm profile cmd test"

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
    tst_resm TINFO "atune-adm profile cmd test"
    # Check all the supported workload
    for ((i=0;i<${#ARRAY_PROFILE[@]};i++));do
        atune-adm profile ${ARRAY_PROFILE[i]} >& temp.log
        check_result $? 0

        grep -i "load profile ${ARRAY_PROFILE[i]} Faild" temp.log
        check_result $? 1

        atune-adm list > temp.log
        grep ${ARRAY_PROFILE[i]} temp.log | grep true
        check_result $? 0
    done

    # Help info
    atune-adm profile -h > temp.log
    grep "active the specified profile and check the actived profile" temp.log
    check_result $? 0

    # The value of the Workload name is special character and ultra long character
    array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS")
    for ((i=0;i<${#array[@]};i++));do
        atune-adm profile ${array[i]} >& temp.log
        check_result $? 1

        grep "load profile .* Faild" temp.log
        check_result $? 0
    done

    # Workload name is null
    atune-adm profile >& temp.log
    grep "only one workloadload type can be set" temp.log
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
