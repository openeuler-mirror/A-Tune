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
# Create: 2020-10-30

if [ "$#" -ne 1 ]; then
  echo "USAGE: $0 ITERATION"
  exit 1
fi

ITERATION=$1

export GOGC=1440
export GOMAXPROCS=56
for ((i = 0; i < ITERATION; i++)); do
  echo 3 >/proc/sys/vm/drop_caches
  go test crypto/ecdsa -run=Bench -benchmem -bench=BenchmarkSignP256
done
