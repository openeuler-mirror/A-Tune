#!/bin/sh
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-10-29

command -v swapoff >/dev/null 2>&1
ret=$?
[ $ret -ne 0 ] && echo "\033[31m command swapoff is not exist \033[31m" && exit 1

command -v swapon >/dev/null 2>&1
ret=$?
[ $ret -ne 0 ] && echo "\033[31m command swapon is not exist \033[31m" && exit 1

value=$(echo "$@" | awk '{$NF="";print}')
option=$(echo "$@" | awk '{print $NF}')
case "$option" in
"off")
  swapoff $(eval echo "$value")
  ;;
"on")
  swapon $(eval echo "$value")
  ;;
*)
  echo "\033[31m this command option is not supported \033[31m" && exit 1
  ;;
esac

