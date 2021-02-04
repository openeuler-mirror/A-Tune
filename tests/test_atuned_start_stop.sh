#!/bin/sh
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
#
# The implementation was written so as to confirm atuned services.
#
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-12-26

export TCID="atuned"

. ./test_lib.sh

init()
{
    echo "init the system"
    systemctl stop atuned
}

cleanup()
{
    echo "===================="
    echo "Clean the System"
    echo "===================="
    systemctl start atuned
}

test01()
{
    tst_resm TINFO "service start/stop"

    systemctl start atuned
    systemctl status atuned | grep -w active | grep -w running
    ret1=$?
    systemctl stop atuned
    systemctl status atuned | grep -w inactive | grep  -w dead
    ret2=$?
    if [ $ret1 == 0 ] && [ $ret2 == 0 ];then
            tst_resm TPASS "service start/stop"
    else
            tst_resm TFAIL "service start/stop"
    fi

}

TST_CLEANUP=cleanup

init

test01

tst_exit

