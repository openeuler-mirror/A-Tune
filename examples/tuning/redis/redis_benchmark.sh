#!/usr/bin/bash
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.

#############################################
# @Author    :   shangyingjie
# @Contact   :   yingjie@isrc.iscas.ac.cn
# @Date      :   2022/3/6
# @License   :   Mulan PSL v2
# @Desc      :   Redis benchmark trigger script
# #############################################

echo 'triggering benchmark...'
cd "$(dirname "$0")"

redis_benchmark_ip='will be replaced after running prepare.sh'
if [ -f "./benchmark_host_key" ]; then
    ssh -i benchmark_host_key root@"$redis_benchmark_ip" -t "/usr/bin/python3 /root/benchmark.py"
    scp -i benchmark_host_key root@"$redis_benchmark_ip":/root/redis_benchmark.log ./
else
    ssh root@"$redis_benchmark_ip" -t "/usr/bin/python3 /root/benchmark.py"
    scp root@"$redis_benchmark_ip":/root/redis_benchmark.log ./
fi
