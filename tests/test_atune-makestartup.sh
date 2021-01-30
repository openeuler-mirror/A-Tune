#!/bin/sh
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
#
# The implementation was written so as to confirm one-click start.
#
# A-Tune is licensed under the Mulan PSL v2,
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2020-10-14

export TCID="make startup"

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
    rm -rf startup_file
}


test01()
{
    tst_resm TINFO "startup"
    cd ..
    make startup
    ret1=$?
    systemctl is-active atuned  > startup_file
    startup=`cat startup_file`
    ret2=$?
    if [ $ret1 == 0 ] && [ $ret2 == 0 ] && [[ "$startup" == "active" ]]; then
         tst_resm TPASS "startup"
    else
         tst_resm TFAIL "startup"
    fi
}


TST_CLEANUP=cleanup

init

test01

tst_exit

