#!/bin/sh
# Copyright (c) The Lab of Professor Weiwei Lin (linww@scut.edu.cn),
# School of Computer Science and Engineering, South China University of Technology.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2021-01-04

path=$(
  cd "$(dirname "$0")"
  pwd
)

echo "update the client and server yaml files"
sed -i "s#python3 .*/key_parameters_select_variant.py#python3 $path/key_parameters_select_variant.py#g" $path/key_parameters_select_variant_client.yaml
sed -i "s#cat .*/key_parameters_select_variant.py#cat $path/key_parameters_select_variant.py#g" $path/key_parameters_select_variant_server.yaml
sed -i "s#' .*/key_parameters_select_variant.py#' $path/key_parameters_select_variant.py#g" $path/key_parameters_select_variant_server.yaml

echo "copy the server yaml file to /etc/atuned/tuning/"
cp $path/key_parameters_select_variant_server.yaml /etc/atuned/tuning/


