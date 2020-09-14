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
# Create: 2020-01-13
# Author: zhangtaibo <sonice1755@163.com>

export TCID="atune-adm undefine cmd test"

. ./test_lib.sh
test_service="test_service"
test_app="test_app"
test_scenario="test_scenario"
profile_path="./conf/example.conf"

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
    tst_resm TINFO "atune-adm undefine cmd test"
    # Check undefine function
    atune-adm define $test_service $test_app $test_scenario $profile_path
    atune-adm list > temp.log
    grep "$test_service" temp.log | grep "$test_app-$test_secnario"
    check_result $? 0

    # delete self define workload
    atune-adm undefine $test_service-$test_app-$test_scenario
    atune-adm list > temp.log
    grep "$test_service" temp.log | grep "$test_app-$test_secnario"
    check_result $? 1

    # Help info
    atune-adm undefine -h > temp.log
    grep "delete the specified profile" temp.log
    check_result $? 0

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi
}

test02()
{
    tst_resm TINFO "atune-adm undefine WorkloadType input test"
    # Check all the supported workload
    for ((i=0;i<${#ARRAY_PROFILE[@]};i++));do
        atune-adm undefine ${ARRAY_PROFILE[i]} >& temp.log
        check_result $? 0

        grep "only self defined type can be deleted" temp.log
        check_result $? 0
    done

    # The input of the workload_type is special character, ultra long character and null
    local array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "")
    local i=0
    for ((i=0;i<${#array[@]};i++));do
        atune-adm undefine ${array[i]}  >& temp.log
        case ${array[i]} in
            "$SPECIAL_CHARACTERS")
                check_result $? 1
                grep "input:.* is invalid" temp.log;;
            $ULTRA_LONG_CHARACTERS)
                check_result $? 0
                grep "only self defined type can be deleted" temp.log;;
            *)
                check_result $? 1
                grep "Incorrect Usage." temp.log
        esac
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
test02

tst_exit

