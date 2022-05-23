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
# @Date      :   2022/5/21
# @License   :   Mulan PSL v2
# @Desc      :   Kafka deployment script
# #############################################

cd "$(dirname "$0")"

while [[ -z "$kafka_server_ip" ]]; do
    read -p "please input kafka-server(localhost) IP:" kafka_server_ip
done

while [[ -z "$kafka_client_ip" ]]; do
    read -p "please input kafka-client IP:" kafka_client_ip
done
read -p "enter y to set up new ssh keys for the kafka-client or skip if already deployed:" setup_new_ssh_key

if [ "$setup_new_ssh_key" = "y" ]; then
    ssh-keygen -t rsa -f client_ssh_key -N ""
    ssh-copy-id -i client_ssh_key root@"$kafka_client_ip"
fi

echo "update launcher_on_server.sh and benchmark_on_client.sh with value just entered..."
sed -i "s#KAFKA_SERVER_IP=.*#KAFKA_SERVER_IP=$kafka_server_ip#g" benchmark_on_client.sh
sed -i "s#KAFKA_CLIENT_IP=.*#KAFKA_CLIENT_IP=$kafka_client_ip#g" launcher_on_server.sh

echo "copy benchmark script to kafka-client" "$kafka_client_ip"
if [ "$setup_new_ssh_key" = "y" ]; then
    scp -i client_ssh_key benchmark_on_client.sh root@"$kafka_client_ip":/root/
else
    scp benchmark_on_client.sh root@"$kafka_client_ip":/root/
fi

if [ -f "./kafka_2.13-3.2.0.tgz" ]; then
    echo "Kafka release exist on local."
else
    echo "download Kafka release on kafka-server."
    wget https://dlcdn.apache.org/kafka/3.2.0/kafka_2.13-3.2.0.tgz
fi

echo "copy Kafka release to kafka-client."
scp ./kafka_2.13-3.2.0.tgz root@"$kafka_client_ip":/root/

echo "install tar and jdk runtime on kafka-server"
yum install -y tar java
echo "install tar and jdk runtime on kafka-client"
ssh -i client_ssh_key -t root@"$kafka_client_ip" "yum install -y tar java;"

echo "extract Kafka release tarball on kafka-server."
tar -xzf ./kafka_2.13-3.2.0.tgz
echo "extract Kafka release tarball on kafka-client."
ssh -i client_ssh_key -t root@"$kafka_client_ip" "tar -xzf /root/kafka_2.13-3.2.0.tgz"

echo "modify kafka server configuration"
echo "listeners=PLAINTEXT://0.0.0.0:9092 \
advertised.listeners=PLAINTEXT://$KAFKA_SERVER_IP:9092" >>./kafka_2.13-3.2.0/config/server.properties

echo "start kafka service"
bash ./manager.sh --start

echo "create topic for benchmark"
bash ./manager.sh --create-topic
