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
# Create: 2020-02-09

profile=/etc/profile
hisi_conf=$(cat "$profile" | grep -w "HISI_CONF_ENV" | awk -F "=" '{print $2}')
openss_lconf=$(cat "$profile" | grep -w "OPENSSL_CONF" | awk -F "=" '{print $2}')
if [ "$hisi_conf" != "" -a "$openss_lconf" != "" ]; then
  echo 1
else
  echo 0
fi

