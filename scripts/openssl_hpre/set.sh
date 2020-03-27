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
HPRE_HOME_PATH=$(
  cd "$(dirname "$0")"
  pwd
)

if [ $# != 1 ]; then
  echo "Usage: ${SCRIPT} 1:enable or 0:disable"
  exit 1
fi

if [ "$1" == "1" ]; then
  #echo "Enable hpre"
  if lspci | grep -q 'HPRE'; then
    echo "    [check] This machine support HPRE device!"
  else
    echo "\033[31m This Machine can not support HPRE, try to upgrade bios to version 3.24.01 and re-power on the machine \033[0m"
    exit 1
  fi

  if openssl version | grep -q 'OpenSSL'; then
    echo "    [check] The openssl is installed, make sure its version is newer than 1.1.1"
  else
    echo "\033[31m NO openssl is installed, please installed it firstly! \033[31m"
    exit 1
  fi

  if lsmod | grep -q 'hisi_hpre'; then
    echo "    [check] The hpre kernel driver is detected"
  else
    echo "\033[31m No hpre kernel driver is detected, install the hpre driver firstlly! \033[31m"
    exit 1
  fi

  if ls /usr/lib64/engines-1.1/ | grep -q "hpre2.so"; then
    echo "    [check] Detect the hpre2 engine in the openssl engine libs"
  else
    echo "\033[31m No hpre2 engine in the openssl engine libs, install hpre2 engine into the openssl engine libs  \033[31m"
    exit 1
  fi

  if ls /usr/lib64 | grep -q "libwd.*"; then
    echo "    [check] Detect the Union Acceleration Framework libwd.* in the /usr/lib64"
  else
    echo "\033[31m No Union Acceleration Framework is detected, install it to use hpre! \033[31m"
    exit 1
  fi

  orig_openssl_conf=$(openssl version -d | awk '{print $2}' | sed 's/\"//g')
  if [ ! -d "$orig_openssl_conf" ]; then
    echo "Failed to Get orig openssl conf file: $orig_openssl_conf"
  fi

  orig_openssl_conf=$orig_openssl_conf"/openssl.cnf"
  cat "${HPRE_HOME_PATH}"/openssl.cnf >"${HPRE_HOME_PATH}"/openssl_hpre.cnf
  cat "$orig_openssl_conf" >>"${HPRE_HOME_PATH}"/openssl_hpre.cnf

  export HISI_CONF_ENV=${HPRE_HOME_PATH}
  export OPENSSL_CONF=${HPRE_HOME_PATH}/openssl_hpre.cnf

  sed -i '/export OPENSSL_CONF=/d' /etc/profile
  sed -i '/export HISI_CONF_ENV=/d' /etc/profile

  echo "export HISI_CONF_ENV=${HPRE_HOME_PATH}" >>/etc/profile
  echo "export OPENSSL_CONF=${HPRE_HOME_PATH}/openssl_hpre.cnf" >>/etc/profile

  source /etc/profile
  echo -e "\033[31m Please execute cmd 'source /etc/profile' and restart application (e.g. nginx) to make hpre in use! \033[0m"

else
  echo "Disable hpre"

  sed -i '/export OPENSSL_CONF=/d' /etc/profile
  sed -i '/export HISI_CONF_ENV=/d' /etc/profile

  echo "export HISI_CONF_ENV=" >>/etc/profile
  echo "export OPENSSL_CONF=" >>/etc/profile
fi

