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
# Create: 2020-01-13
# Author: zhangtaibo <sonice1755@163.com>

export TCID="atune-adm define cmd test"

. ./test_lib.sh
self_workload="self_workload"
profile_name="self_profile"
profile_file="./conf/example.conf"

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
    tst_resm TINFO "atune-adm define cmd test"
    # Check define function
    atune-adm define $self_workload $profile_name $profile_file
    atune-adm list > temp.log
    grep "$self_workload" temp.log | grep "$profile_name"
    check_result $? 0

    # define the same workload
    atune-adm define $self_workload $profile_name $profile_file > temp.log
    grep "$self_workload is already exist" temp.log
    check_result $? 0

    # Help info
    atune-adm define -h > temp.log
    grep "create a new workload type which can not be already exist" temp.log
    check_result $? 0

    if [ $EXIT_FLAG -ne 0 ];then
        tst_resm TFAIL
    else
        tst_resm TPASS
    fi

    # delete self define workload
    atune-adm undefine $self_workload
}

test02()
{
    tst_resm TINFO "atune-adm define WorkloadType input test"
    # Check all the supported workload
    for ((i=0;i<${#ARRAY_WORKLOADTYPE[@]};i++));do
        atune-adm define ${ARRAY_WORKLOADTYPE[i]} $profile_name $profile_file >& temp.log
        check_result $? 0

        grep "${ARRAY_WORKLOADTYPE[i]} is already exist" temp.log
        check_result $? 0
    done

    # The input of the workload_type is special character, ultra long character and null
    local array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "")
    local i=0
    for ((i=0;i<${#array[@]};i++));do
        if [ -z ${array[i]} ];then
            atune-adm define ${array[i]} $profile_name $profile_file >& temp.log
            check_result $? 1
            grep -i "Incorrect Usage." temp.log
        else
            atune-adm define ${array[i]} $profile_name $profile_file >& temp.log
            check_result $? 0
            atune-adm list > temp.log
            grep "$profile_name" temp.log
            check_result $? 0
            atune-adm undefine ${array[i]}
        fi
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
    for ((i=0;i<${#ARRAY_PROFILE_NAME[@]};i++));do
        atune-adm define $self_workload ${ARRAY_PROFILE_NAME[i]} $profile_file >& temp.log
        check_result $? 0

        grep "${ARRAY_PROFILE_NAME[i]} is already exist" temp.log
        check_result $? 0
    done

    # The input of the workload_type is special character, ultra long character and null
    local array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "")
    local i=0
    for ((i=0;i<${#array[@]};i++));do
        if [ -z ${array[i]} ];then
            atune-adm define $self_workload ${array[i]} $profile_file >& temp.log
            check_result $? 1
            grep -i "Incorrect Usage." temp.log
        else
            atune-adm define $self_workload ${array[i]} $profile_file >& temp.log
            check_result $? 0
            atune-adm list > temp.log
            grep "$self_workload" temp.log
            check_result $? 0
            atune-adm undefine $self_workload
        fi
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

