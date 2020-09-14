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
# Create: 2020-01-08
# Author: zhangtaibo <sonice1755@163.com>

export TCID="atuned.cnf module configuration test"

. ./test_lib.sh

init()
{
    echo "init the system"
    cp -a  $ATUNE_CONF $ATUNE_CONF.bak
    # Reduce the numbers of collected data, reduce testcase running time
    change_conf_value sample_num 2
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
    tst_resm TINFO "atuned.cnf file's module configuration test"
    # The value of the module configuration is mem_topo,cpu_topo,net_topo,storage_topo and multiple topo
    array=("mem_topo" "cpu_topo" "net_topo" "storage_topo" "mem_topo, cpu_topo, net_topo, storage_topo")
    for ((i=0;i<${#array[@]};i++));do
        rm -rf /usr/share/atuned/checker/*
        change_conf_value module ${array[i]}
        systemctl restart $ATUNE_SERVICE_NAME
        check_result $? 0

        wait_service_ready $ATUNE_SERVICE_NAME
        # multiple topo case
        if [ `expr index "${array[i]}" ","` -ne 0 ];then
            arr=(${array[i]//,/})
            for ((j=0;j<${#arr[@]};j++));do
                wait_condition 10 'ls -l /usr/share/atuned/checker/${arr[j]}.xml'
                ls -l /usr/share/atuned/checker/${arr[j]}.xml
                check_result $? 0
            done
        else
            wait_condition 10 'ls -l /usr/share/atuned/checker/${array[i]}.xml'
            check_result $? 0
        fi

        atune-adm analysis
        check_result $? 0

    done

    # The value of the module configuration is special character and ultra long character and null
    array1=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "")
    for ((i=0;i<${#array1[@]};i++));do
        rm -rf /usr/share/atuned/checker/*
        change_conf_value module ${array1[i]}
        atune-adm rollback # default profile will check environment, so rollback to init.
        systemctl restart $ATUNE_SERVICE_NAME
        check_result $? 0

        wait_service_ready $ATUNE_SERVICE_NAME
        wait_condition 10 'ls -l /usr/share/atuned/checker/*_topo.xml'
        check_result $? 1
        ls -l /usr/share/atuned/checker/

        atune-adm analysis
        check_result $? 0
    done

    # Comment module configuration
    rm -rf /usr/share/atuned/checker/*
    comment_conf_value module
    systemctl restart $ATUNE_SERVICE_NAME
    check_result $? 0

    wait_service_ready $ATUNE_SERVICE_NAME
    xml_files=`ls -l /usr/share/atuned/checker/*.xml | wc -l`
    if [ $xml_files -ne 0 ];then
        ((EXIT_FLAG++))
    fi
    ls -l /usr/share/atuned/checker/

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
