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

SCRIPT=$(basename $0)
SCRIPT_PATH=$(
  cd "$(dirname "$0")"
  pwd
)

if [ $# != 1 ]; then
  echo "Usage: ${SCRIPT} on or off"
  exit 1
fi

lsmod | grep prefetch_tuning &>/dev/null
uninstall=$?

case "$1" in
"on")
  policy=15
  ;;
"off")
  policy=0
  ;;
"reset")
  if [ ${uninstall} = 0 ]; then
    rmmod prefetch_tuning
  fi
  exit 0
  ;;
*)
  exit 2
  ;;
esac

if [ ${uninstall} != 0 ]; then
  insmod /lib/modules/prefetch_tuning/prefetch_tuning.ko
  [ $? != 0 ] && exit 3
fi

echo ${policy} >/sys/class/misc/prefetch/policy
[ $? != 0 ] && exit 4

exit 0

