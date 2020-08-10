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
# Create: 2020-08-08

command -v hdparm >/dev/null 2>&1
ret=$?
[ $ret -ne 0 ] && echo "\033[31m command hdparm is not exist \033[31m" && exit 1

disk=$(echo "$@" | awk '{$NF="";print}')
option=$(echo "$@" | awk '{print $NF}')
case "$option" in
"off")
  hdparm -W 0 $(eval echo "/dev/$disk")
  ;;
"on")
  hdparm -W 1 $(eval echo "/dev/$disk")
  ;;
*)
  echo "\033[31m this command option is not supported \033[31m" && exit 1
  ;;
esac
