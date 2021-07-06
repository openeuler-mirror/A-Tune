#!/bin/sh
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

ps -ef | grep pd-server | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep tikv-server | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep tidb-server | grep -v grep | awk '{print $2}' | xargs kill -9
