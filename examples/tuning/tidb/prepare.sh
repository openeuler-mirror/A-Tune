#!/usr/bin/bash
# Copyright (c) 2021 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2021-06-03

echo "copy the tikv_config_base.toml file to tikv_config.toml"
rm ./tikv_config.toml -f
cp ./tikv_config_base.toml ./tikv_config.toml
echo "copy the server yaml file to /etc/atuned/tuning/"
cp ./tidb_server.yaml /etc/atuned/tuning/
echo "copy the tidb.sh file to /tmp/"
cp ./tidb.sh /tmp/
