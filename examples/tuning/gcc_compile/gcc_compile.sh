#!/bin/sh
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2020-09-01

path=$(
  cd "$(dirname "$0")"
  pwd
)
echo "current run path is $path"

tune=generic
option=O0
array_size=20000000
times=10
offset=1024
isarch=no
if [[ $isarch == "yes" ]]; then
  arch="-march=native"
fi
isopenmp=no
if [[ $isopenmp == "yes" ]]; then
  openmp="-fopenmp"
fi

gcc -mtune=$tune $arch -$option $openmp -DSTREAM_ARRAY_SIZE=$array_size -DNTIMES=$times -DOFFSET=$offset $path/stream.c -o $path/stream.o
$path/stream.o
echo "file size: `wc -c $path/stream.o`"
rm -rf $path/stream.o
