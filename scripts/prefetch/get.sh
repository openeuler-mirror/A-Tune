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

lsmod | grep prefetch_tuning &> /dev/null
[ $? != 0 ] && echo "reset" && exit 0

policy=$(cat /sys/class/misc/prefetch/policy | awk '{print $2}'| sort -u)
case "$policy" in
	"15")
		echo "on"
		;;
	"0")
		echo "off"
		;;
	*)
		echo "reset"
		;;
esac

exit 0

