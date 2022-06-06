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
# @Date      :   2022/6/20
# @License   :   Mulan PSL v2
# @Desc      :   Kafka deployment script
# #############################################

while [[ -z "$working_directory" ]]; do
    read -p "please specify working directory(absolute path):" working_directory
done

while [[ -z "$atune_directory" ]]; do
    read -p "please specify atune directory(absolute path):" atune_directory
done

kafka_dir=$working_directory/kafka
kafka_server_config=$kafka_dir/config/server.properties
kafka_tuning_yaml=$atune_directory/examples/tuning/kafka

while [[ -z "$kafka_server_ip" ]]; do
    read -p "please input kafka-server(localhost) IP:" kafka_server_ip
done

while [[ -z "$kafka_client_ip" ]]; do
    read -p "please input kafka-client IP:" kafka_client_ip
done
read -p "enter y to set up new ssh keys for the kafka-client or skip if already deployed:" setup_new_ssh_key

if [ "$setup_new_ssh_key" = "y" ]; then
    ssh-keygen -t rsa -f $working_directory/client_ssh_key -N ""
    ssh-copy-id -i $working_directory/client_ssh_key root@"$kafka_client_ip"
fi

echo "update manager.sh, launcher_on_server.sh and benchmark_on_client.sh with value just entered..."
sed -i "s#KAFKA_DIR=.*#KAFKA_DIR=$kafka_dir#g" $working_directory/manager.sh
sed -i "s#working_dir=.*.#working_dir=$working_directory#g" $atune_directory/kafka_client.yaml
sed -i "s#working_dir=.*.#working_dir=$working_directory#g" $atune_directory/kafka_server.yaml
sed -i "s#KAFKA_SERVER_IP=.*#KAFKA_SERVER_IP=$kafka_server_ip#g" $working_directory/benchmark_on_client.sh
sed -i "s#KAFKA_CLIENT_IP=.*#KAFKA_CLIENT_IP=$kafka_client_ip#g" $working_directory/launcher_on_server.sh

echo "copy benchmark script to kafka-client" "$kafka_client_ip"
if [ "$setup_new_ssh_key" = "y" ]; then
    scp -i $working_directory/client_ssh_key $working_directory/benchmark_on_client.sh root@"$kafka_client_ip":/root/
else
    scp $working_directory/benchmark_on_client.sh root@"$kafka_client_ip":/root/
fi

if [ -f "$working_directory/kafka_2.13-3.2.0.tgz" ]; then
    echo "Kafka release exist on local."
else
    echo "download Kafka release on kafka-server."
    wget https://dlcdn.apache.org/kafka/3.2.0/kafka_2.13-3.2.0.tgz
fi

echo "copy Kafka release to kafka-client."
scp -i $working_directory/client_ssh_key $working_directory/kafka_2.13-3.2.0.tgz root@"$kafka_client_ip":/root/

echo "install tar and jdk runtime on kafka-server"
yum install -y tar java
echo "install tar and jdk runtime on kafka-client"
ssh -i $working_directory/client_ssh_key -t root@"$kafka_client_ip" "yum install -y tar java;"

echo "extract Kafka release tarball on kafka-server."
tar -xzf $working_directory/kafka_2.13-3.2.0.tgz
mv $working_directory/kafka_2.13-3.2.0/ $working_directory/kafka

echo "extract Kafka release tarball on kafka-client."
ssh -i $working_directory/client_ssh_key -t root@"$kafka_client_ip" "tar -xzf /root/kafka_2.13-3.2.0.tgz"

echo "modify kafka server configuration"
echo "listeners=PLAINTEXT://0.0.0.0:9092
advertised.listeners=PLAINTEXT://$kafka_server_ip:9092" >>$kafka_server_config
echo "# A-Tune tuning paramters
message.max.bytes=1048588
buffer.memory=33554432
linger.ms=0
max.in.flight.requests.per.connection=5
delivery.timeout.ms=120000" >>$kafka_server_config

echo "start kafka service"
bash $working_directory/manager.sh --start

echo "create topic for benchmark"
bash $working_directory/manager.sh --create-topic
