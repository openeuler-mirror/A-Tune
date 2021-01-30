#!/bin/sh
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
#
# The implementation was written so as to confirm whether to make yaml.
#
# A-Tune is licensed under the Mulan PSL v2,
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2020-10-15

export TCID="make tunning yaml"

. ./test_lib.sh

init()
{
    echo "init the system"
}

cleanup()
{
    echo "===================="
    echo "Clean the System"
    echo "===================="
    rm -rf yaml_file
}


test01()
{
    tst_resm TINFO "make tunning yaml"
    pip3 install openpyxl
    cd ../tools/translate_yaml/
    python3 translate.py -i ../../tuning/csv/ -o ../../tools/translate_yaml > yaml_file
    ret1=$?
    startup=`cat yaml_file | grep FAILED`
    if [ $ret1 == 0 ] && [[ "$startup" == "" ]]; then
         tst_resm TPASS "make tunning yaml"
    else
         tst_resm TFAIL "make tunning yaml"
    fi
}


TST_CLEANUP=cleanup

init

test01

tst_exit

