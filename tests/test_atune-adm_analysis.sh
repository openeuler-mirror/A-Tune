#!/bin/sh
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
#
# The implementation was written so as to confirm atune-adm.
#
# A-Tune is licensed under the Mulan PSL v1,
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
# Create: 2019-12-26

export TCID="atune-adm analysis"

. ./test_lib.sh

init()
{
    echo "init the sysytem"
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

test02()
{
    tst_resm TINFO "analysis  is interruptted"

    atune-adm analysis &
    analysis_pid=$!
    sleep 3
    kill -9 ${analysis_pid}
    atune-adm analysis
    ret2=$?
    if [ $ret2 == 0 ];then
        tst_resm TPASS "analysis is interruptted"
    else
        tst_resm TFAIL "analysis is interruptted"
    fi

}

TST_CLEANUP=cleanup

init

test01
test02

tst_exit

