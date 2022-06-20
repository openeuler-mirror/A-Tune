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
# @Desc      :   Kafka management script
# #############################################

USAGE="Usage: task_manager [OPTION]
--start        start kafka and zookeeper instance
--stop         stop kafka and zookeeper instance
--restart      delete benchmark topic and create new one, stop kafka and zookeeper instance, then start them.
--list-topic   list existing topic
--create-topic create topic: kafka-benchmark
--delete-topic delete topic: kafka-benchmark
--help         output this usage"

KAFKA_DIR="will be replaced after running prepare.sh"
ZOOKEEPER_SERVER_START_SCRPIT=$KAFKA_DIR/bin/zookeeper-server-start.sh
ZOOKEEPER_SERVER_STOP_SCRPIT=$KAFKA_DIR/bin/zookeeper-server-stop.sh
ZOOKEEPER_CONFIG=$KAFKA_DIR/config/zookeeper.properties
KAFKA_SERVER_START_SCRPIT=$KAFKA_DIR/bin/kafka-server-start.sh
KAFKA_SERVER_STOP_SCRPIT=$KAFKA_DIR/bin/kafka-server-stop.sh
KAFKA_SERVER_CONFIG=$KAFKA_DIR/config/server.properties
KAFKA_TOPIC_SCRIPT=$KAFKA_DIR/bin/kafka-topics.sh

if [[ $# -gt 0 ]]; then
  case $1 in
  --start)
    echo "start zookeeper"
    $ZOOKEEPER_SERVER_START_SCRPIT $ZOOKEEPER_CONFIG >/dev/null 2>&1 &
    zookeeper_pid=$!

    echo "start kafka"
    $KAFKA_SERVER_START_SCRPIT $KAFKA_SERVER_CONFIG >/dev/null 2>&1 &
    kafka_pid=$!

    echo "zookeeper_pid: $zookeeper_pid
    kafka_pid: $kafka_pid" >./process_info

    sleep 5s

    cat ./process_info
    exit 0
    ;;
  --stop)
    echo "stop kafka"
    $KAFKA_SERVER_STOP_SCRPIT

    sleep 5s

    echo "stop zookeeper"
    $ZOOKEEPER_SERVER_STOP_SCRPIT

    cat ./process_info
    exit 0
    ;;
  --clean)
    echo "remove /tmp/kafka-logs"
    rm -rf /tmp/kafka-logs/
    exit 0
    ;;
  --delete-topic)
    echo "delete topic: kafka-benchmark"
    $KAFKA_TOPIC_SCRIPT \
      --bootstrap-server=localhost:9092 \
      --delete \
      --topic kafka-benchmark
    exit 0
    ;;
  --create-topic)
    echo "create topic for benchmark, topic: kafka-benchmark"
    $KAFKA_TOPIC_SCRIPT \
      --bootstrap-server 127.0.0.1:9092 \
      --create \
      --topic kafka-benchmark \
      --partitions 6 \
      --replication-factor 1 \
      --config retention.ms=3600000
    exit 0
    ;;
  --list-topic)
    echo "existing topics:"
    $KAFKA_TOPIC_SCRIPT \
      --bootstrap-server=localhost:9092 \
      --list
    exit 0
    ;;
  --restart)
    if [ ! -e "./process_info" ]; then
      echo "kafka is not running!"
      exit 1
    fi

    echo "restart kafka service"
    bash ./manager.sh --delete-topic
    bash ./manager.sh --create-topic
    bash ./manager.sh --stop
    bash ./manager.sh --start
    sleep 5s
    exit 0
    ;;
  --help)
    echo "${USAGE}"
    exit 0
    ;;
  --*)
    echo "Unknown option $1"
    echo "${USAGE}"
    exit 1
    ;;
  esac
fi
