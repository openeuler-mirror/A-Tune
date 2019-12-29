#!/bin/sh
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v1.
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
# Create: 2019-10-29

if [ $# -lt 1 ]
then
    echo "Usage: `basename $0` interval"
    exit 1
fi

interval=$1

files=(/proc/sys/kernel/threads-max /proc/sys/fs/file-nr /proc/loadavg)

for file in ${files[@]}
do
    echo -n \"${file}\",
done
echo ""

while :
do
    for file in ${files[@]}
    do
        echo -n \"`cat ${file}`\",
    done
    echo ""
    sleep ${interval}
done
