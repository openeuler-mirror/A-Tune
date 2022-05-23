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

# #############################################
# @Author    :   shangyingjie
# @Contact   :   yingjie@isrc.iscas.ac.cn
# @Date      :   2022/5/23
# @License   :   Mulan PSL v2
# @Desc      :   kafka benchmark script
# #############################################

KAFKA_DIR=/root/kafka_2.13-3.2.0
KAFKA_PRODUCER_TEST=$KAFKA_DIR/bin/kafka-producer-perf-test.sh
KAFKA_CONSUMER_TEST=$KAFKA_DIR/bin/kafka-consumer-perf-test.sh
KAFKA_SERVER_IP='will be replaced after running prepare.sh'
KAFKA_SERVER_PORT=9092

function get_producer_test_result() {
    output=$(
        $KAFKA_PRODUCER_TEST \
            --topic kafka-benchmark \
            --throughput -1 \
            --num-records 1000000 \
            --record-size 1024 \
            --producer-props acks=all bootstrap.servers="$KAFKA_SERVER_IP":"$KAFKA_SERVER_PORT"
    )
    result_line=$(grep '1000000' <<<"$output")
    arr=($result_line)
    echo "${arr[3]}"
}

function get_consumer_test_result() {
    output=$(
        $KAFKA_CONSUMER_TEST \
            --topic kafka-benchmark \
            --broker-list "$KAFKA_SERVER_IP":"$KAFKA_SERVER_PORT" \
            --messages 1000000
    )
    result_line=$(awk 'FNR == 2' <<<"$output")
    IFS=',' read -r -a arr <<<"$result_line"
    echo "${arr[5]}"
}

producer_test_result=$(get_producer_test_result)
consumer_test_result=$(get_consumer_test_result)
sum=$(echo "$producer_test_result + $consumer_test_result" | bc)
echo "$sum" >/root/kafka_benchmark.log
