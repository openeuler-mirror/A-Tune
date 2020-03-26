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
# Create: 2020-02-06

RUN_HOME=$(
  cd "$(dirname "$0")"
  pwd
)
source "$RUN_HOME"/common.sh

command -v ethtool >/dev/null 2>&1
ret=$?
[ $ret -ne 0 ] && echo "\033[31m command ethtool is not exist \033[31m" && exit 1

get_ethtool_value "$@"

