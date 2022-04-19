#!/usr/bin/bash

# Copyright (c) 2022 Huawei Technologies Co., Ltd.
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
# @Desc      :   Redis deployment script
# #############################################

cd "$(dirname "$0")"

while [[ -z "$redis_server_ip" ]]; do
    read -p "please input redis-server(localhost) IP:" redis_server_ip
done
read -p "please input port for redis-server(localhost), or skip with default port number(6379):" redis_server_port
if [ -z "$redis_server_port" ]; then
    redis_server_port=6379
fi
while [[ -z "$redis_benchmark_ip" ]]; do
    read -p "please input an another host IP to install redis-benchmark(SSH required):" redis_benchmark_ip
done
# read -p "please input port for redis-server(localhost), or skip with default port number(6379):" redis_server_port
read -p "enter y to set up new ssh keys for the redis-benchmark host or skip if deployed." choice
if [ "$choice" = "y" ]; then
    ssh-keygen -t rsa -f benchmark_host_key -N ""
    ssh-copy-id -i benchmark_host_key root@"$redis_benchmark_ip"
fi

echo "install redis-server..."
yum install -y redis

echo "update redis_benchmark.sh and benchmark.py with value just entered..."
sed -i "s#redis_server_ip=.*#redis_server_ip=$redis_server_ip#g" redis_benchmark.sh
sed -i "s#redis_server_ip = .*#redis_server_ip = '$redis_server_ip'#g" benchmark.py
sed -i "s#redis_server_port=.*#redis_server_port=$redis_server_port#g" redis_benchmark.sh
sed -i "s#redis_server_port = .*#redis_server_port = '$redis_server_port'#g" benchmark.py
sed -i "s#redis_benchmark_ip=.*#redis_benchmark_ip=$redis_benchmark_ip#g" redis_benchmark.sh

echo "copy benchmark scripts to" "$redis_benchmark_ip"
if [ "$choice" = "y" ]; then
    scp -i benchmark_host_key benchmark.py root@"$redis_benchmark_ip":/root/
else
    scp benchmark.py root@"$redis_benchmark_ip":/root/
fi

echo "deploy redis-benchmark on:" "$redis_benchmark_ip"
if [ "$choice" = "y" ]; then
    ssh -i benchmark_host_key -t root@"$redis_benchmark_ip" "yum install -y redis;"
else
    ssh -t root@"$redis_benchmark_ip" "yum install -y redis;"
fi

echo "start redis-server..."
systemctl start redis.service

echo "modify bind port to 0.0.0.0 to allow redis-benchmark access."
sed -i 's/bind 127.0.0.1/bind 0.0.0.0/g' /etc/redis.conf
systemctl restart redis.service

