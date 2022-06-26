#!/bin/sh
# Copyright (c) lingff(ling@stu.pku.edu.cn),
# School of Software & Microelectronics, Peking University.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2021-04-22

path=$(
  cd "$(dirname "$0")"
  pwd
)

echo "install tensorflow"
pip3 install tensorflow -i https://pypi.tuna.tsinghua.edu.cn/simple

echo "first run the python script to download the MNIST dataset"
python3 $path/tensorflow_train.py

echo "update the client and server yaml files"
sed -i "s#python3 .*/tensorflow_train.py#python3 $path/tensorflow_train.py#g" $path/tensorflow_train_client.yaml
sed -i "s#cat .*/tensorflow_train.py#cat $path/tensorflow_train.py#g" $path/tensorflow_train_server.yaml
sed -i "s#' .*/tensorflow_train.py#' $path/tensorflow_train.py#g" $path/tensorflow_train_server.yaml

echo "copy the server yaml file to /etc/atuned/tuning/"
cp $path/tensorflow_train_server.yaml /etc/atuned/tuning/


