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
# Create: 2020-01-07
# Author: zhangtaibo <sonice1755@163.com>

export TCID="atuned.cnf level configuration test"

. ./test_lib.sh

init()
{
    echo "init the system"
    cp -a  $ATUNE_CONF $ATUNE_CONF.bak
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
    tst_resm TINFO "atuned.cnf file's level configuration test"
    # Reduce the numbers of collected data, reduce testcase running time
    change_conf_value sample_num 2

    # The value of the level configuration is debug
    > /var/log/messages
    change_conf_value level debug
    systemctl restart $ATUNE_SERVICE_NAME
    wait_service_ready $ATUNE_SERVICE_NAME
    atune-adm analysis
    check_result $? 0

    grep level=debug /var/log/messages
    check_result $? 0

    # The value of the level configuration is special character and ultra long character and null
    array=("$SPECIAL_CHARACTERS" "$ULTRA_LONG_CHARACTERS" "")
    for ((i=0;i<${#array[@]};i++));do
        > /var/log/messages
        change_conf_value level ${array[i]}
        systemctl restart $ATUNE_SERVICE_NAME
        check_result $? 1

        grep level=debug /var/log/messages
        check_result $? 1
    done

    # Comment level configuration
    > /var/log/messages
    comment_conf_value level
    systemctl restart $ATUNE_SERVICE_NAME
    check_result $? 1

    grep level=debug /var/log/messages
    check_result $? 1

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
