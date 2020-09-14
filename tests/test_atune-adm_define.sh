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

export TCID="atune-adm define cmd test"

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
    tst_resm TINFO "atune-adm define cmd test"
    # Check define function
    atune-adm define $test_service $test_app $test_scenario $profile_path
    atune-adm list > temp.log
    grep "$test_service" temp.log | grep "$test_app-$test_secnario"
    check_result $? 0

    # define the same workload
    atune-adm define $test_service $test_app $test_scenario $profile_path > temp.log
    grep ".* is already exist" temp.log
    check_result $? 0

    # Help info
    atune-adm define -h > temp.log
    grep "atune-adm define - create a new application profile" temp.log
    check_result $? 0

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi

    # delete self define workload
    atune-adm undefine $test_service-$test_app-$test_scenario-$profile_path
}

test02()
{
    tst_resm TINFO "atune-adm define WorkloadType input test"
    # Check all the supported workload
    for ((i=0;i<${#ARRAY_SERVICE[@]};i++));do
        atune-adm define ${ARRAY_SERVICE[i]} $test_app $test_scenario $profile_path >& temp.log
        check_result $? 0

        grep "define a new application profile success" temp.log
        check_result $? 0

        atune-adm undefine ${ARRAY_SERVICE[i]}-$test_app-$test_scenario
    done

    # The input of the workload_type is special character, ultra long character and null
    local array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "")
    local i=0
    for ((i=0;i<${#array[@]};i++));do
        atune-adm define ${array[i]} $test_app $test_scenario $profile_path >& temp.log
        check_result $? 1
        case ${array[i]} in
            "$SPECIAL_CHARACTERS")
                 grep -i "input:.* is invalid" temp.log;;
            $ULTRA_LONG_CHARACTERS)
                grep -i "file name too long" temp.log;;
            *)
                grep -i "Incorrect Usage." temp.log;;
        esac
        check_result $? 0
    done

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi
}

test03()
{
    tst_resm TINFO "atune-adm define profile_name input test"
    # Check all the supported workload
    for ((i=0;i<${#ARRAY_SERVICE[@]};i++));do
        atune-adm define $test_service ${ARRAY_SERVICE[i]} $test_scenario $profile_path >& temp.log
        check_result $? 0

        grep "define a new application profile success" temp.log
        check_result $? 0

        atune-adm undefine $test_service-${ARRAY_SERVICE[i]}-$test_scenario
    done

    # The input of the workload_type is special character, ultra long character and null
    local array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "")
    local i=0
    for ((i=0;i<${#array[@]};i++));do
        atune-adm define $test_service ${array[i]} $test_scenario $profile_path >& temp.log
        check_result $? 1
        case ${array[i]} in
            "$SPECIAL_CHARACTERS")
                grep -i "input:.* is invalid" temp.log;;
            $ULTRA_LONG_CHARACTERS)
                grep -i "file name too long" temp.log;;
            *)
                grep -i "Incorrect Usage." temp.log;;
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
test03

tst_exit

