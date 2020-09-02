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
# Create: 2020-09-01

path=$(
  cd "$(dirname "$0")"
  pwd
)

echo "update the client and server yaml files"
sed -i "s#sh .*/gcc_compile.sh#sh $path/gcc_compile.sh#g" $path/gcc_compile_client.yaml
sed -i "s#-c .*/stream.o#-c $path/stream.o#g" $path/gcc_compile_client.yaml
sed -i "s#cat .*/gcc_compile.sh#cat $path/gcc_compile.sh#g" $path/gcc_compile_server.yaml
sed -i "s#' .*/gcc_compile.sh#' $path/gcc_compile.sh#g" $path/gcc_compile_server.yaml

echo "copy the server yaml file to /etc/atuned/tuning/"
cp $path/gcc_compile_server.yaml /etc/atuned/tuning/
