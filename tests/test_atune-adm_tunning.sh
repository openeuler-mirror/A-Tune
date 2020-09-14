#!/bin/sh
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
#
# The implementation was written so as to confirm atune-adm.
#
# A-Tune is licensed under the Mulan PSL v2,
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-12-26

export TCID="atune-adm tuning"

. ./test_lib.sh

init()
{
    echo "init the system"
    if [ -f /etc/atuned/tuning/example-server.yaml ]; then
        cp -ar /etc/atuned/tuning/example-server.yaml /etc/atuned/tuning/example1-server.yaml
        rm -rf /etc/atuned/tuning/example-server.yaml
    fi
    cp -ar tuning_examples/example-server.yaml  /etc/atuned/tuning
    systemctl start atuned
}

cleanup()
{
    echo "===================="
    echo "Clean the System"
    echo "===================="
    rm -rf /etc/atuned/tuning/example-server.yaml
    if [ -f /etc/atuned/tuning/example1-server.yaml ]; then
        cp -ar /etc/atuned/tuning/example1-server.yaml /etc/atuned/tuning/example-server.yaml
        rm -rf /etc/atuned/tuning/example1-server.yaml
    fi
    rm -rf tuning_file
    rm -rf temp.log
}


test01()
{
    tst_resm TINFO "tuning project" 

    local str_129="000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    sed -i  "s/example/$str_129/g" tuning_examples/example-client.yaml
    sed -i  "s/example/$str_129/g" /etc/atuned/tuning/example-server.yaml
    atune-adm tuning --project $str_129 tuning_examples/example-client.yaml >& temp.log
    sed -i  "s/$str_129/example/g" tuning_examples/example-client.yaml
    sed -i  "s/$str_129/example/g" /etc/atuned/tuning/example-server.yaml
    grep "no less than 1 and no greater than 128"  temp.log
    ret=$?
    check_result $ret 0
    if [ $ret == 0 ]; then
         tst_resm TPASS "tuning project"
    else
         tst_resm TFAIL "tuning project"
    fi
}

test02()
{
    tst_clean
    tst_resm TINFO "tuning project not exist"

    sed -i  "s/example/example_no_exist/g" tuning_examples/example-client.yaml
    atune-adm tuning --project example_no_exist tuning_examples/example-client.yaml >& tuning_file
    grep "project:example_no_exist not found" tuning_file
    ret1=$?
    check_result $ret1 0
    sed -i "s/example_no_exist/example/g" tuning_examples/example-client.yaml
    atune-adm tuning --project example tuning_examples/example-client.yaml > tuning_file
    ret2=$?
    check_result $ret2 0

    if [ $ret1 == 0 ] && [ $ret2 == 0 ];then
        tst_resm TPASS "tuning project not exist"
    else
        tst_resm TFAIL "tuning project not exist"
    fi
}

test03()
{
    tst_clean
    tst_resm TINFO "tuning project is NULL"

    sed -i  "s/\"example\"//g" tuning_examples/example-client.yaml
    atune-adm tuning --project  tuning_examples/example-client.yaml > tuning_file 2>&1
    cat tuning_file |grep "Incorrect Usage."
    ret1=$?
    check_result $ret1 0
    sed -i "s/project:.*/project: \"example\"/g" tuning_examples/example-client.yaml
    atune-adm tuning --project example tuning_examples/example-client.yaml > tuning_file
    ret2=$?
    check_result $ret2 0

    if [ $ret1 == 0 ] && [ $ret2 == 0 ];then
        tst_resm TPASS "tuning project is NULL"
    else
        tst_resm TFAIL "tuning project is NULL"
    fi
}



TST_CLEANUP=cleanup

init

test01
test02
test03

tst_exit

