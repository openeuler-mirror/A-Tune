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
# @Date      :   2022/5/21
# @License   :   Mulan PSL v2
# @Desc      :   kafka benchmark trigger script
# #############################################

echo 'launch benchmark'

WORKING_DIR="will be replaced after running prepare.sh"
KAFKA_CLIENT_IP='will be replaced after running prepare.sh'

if [ -f "./client_ssh_key" ]; then
    ssh -i $WORKING_DIR/client_ssh_key root@"$KAFKA_CLIENT_IP" -t "/usr/bin/bash /root/benchmark_on_client.sh"
    scp -i $WORKING_DIR/client_ssh_key root@"$KAFKA_CLIENT_IP":/root/kafka_benchmark.log ./
else
    ssh root@"$KAFKA_CLIENT_IP" -t "/usr/bin/bash /root/benchmark_on_client.sh"
    scp root@"$KAFKA_CLIENT_IP":/root/kafka_benchmark.log ./
fi
