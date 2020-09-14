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

export TCID="atune-adm analysis"

. ./test_lib.sh

init()
{
    echo "init the system"
    systemctl start atuned
}

cleanup()
{
    echo "===================="
    echo "Clean the System"
    echo "===================="
    rm -rf analysis_file
}


test01()
{
    tst_resm TINFO "analysis"

    atune-adm analysis > analysis_file
    ret1=$?
    workload=`cat analysis_file | grep "Current System Workload Characterization" | awk '{print $(NF-1)}'`
    atune-adm list |grep -w  $workload |grep true
    ret2=$?
    if [ $ret1 == 0 ] && [ $ret2 == 0 ]; then
         tst_resm TPASS "analysis"
    else
         tst_resm TFAIL "analysis"
    fi
}


TST_CLEANUP=cleanup

init

test01

tst_exit

