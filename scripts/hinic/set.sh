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
# Create: 2020-02-24

SCRIPT=$(basename "$0")
if [ $# != 1 ]; then
  echo "Usage: ${SCRIPT} number or disable"
  exit 1
fi

path="/etc/modprobe.d/hinic.conf"
case "$1" in
"disable")
  lsmod | grep hinic &>/dev/null
  ret=$?
  [ $ret -eq 0 ] && rmmod hinic
  exit 0
  ;;
"2" | "4" | "8" | "16")
  [ ! -f "$path" ] && touch "$path"
  sed -i '/options hinic rx_buff=/d' "$path"
  echo "options hinic rx_buff=$1" >>"$path"
  lsmod | grep hinic &>/dev/null
  ret=$?
  [ $ret -eq 0 ] && rmmod hinic
  modprobe hinic
  ;;
*)
  echo "\033[31m this option is not supported \033[31m" && exit 1
  ;;
esac
