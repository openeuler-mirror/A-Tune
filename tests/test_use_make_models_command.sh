#!/bin/sh
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
#
# The implementation was written so as to confirm whether to make models.
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

export TCID="make models"

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
    rm -rf models_file
    sed -i 's/#export GOMP_CPU_AFFINITY.*$/export GOMP_CPU_AFFINITY=0-$[CPUNO - 1]/g' /etc/profile.d/performance.sh
    cd ..
    make startup
}


test01()
{
    tst_resm TINFO "make models"
    cd ..
    make models
    ret1=$?
    str=`cat /etc/profile.d/performance.sh | grep GOMP_CPU_AFFINITY`
    sed -i 's/export GOMP_CPU_AFFINITY.*$/#export GOMP_CPU_AFFINITY=0-$[CPUNO - 1]/g' /etc/profile.d/performance.sh
    make startup
    cd tools/
    python3 generate_models.py -d ../analysis/dataset -m ../analysis/models
    ret2=$?
    if [ $ret1 == 0 ] && [ $ret2 == 0 ]; then
         tst_resm TPASS "make models"
    else
         tst_resm TFAIL "make models"
    fi
}


TST_CLEANUP=cleanup

init

test01

tst_exit
