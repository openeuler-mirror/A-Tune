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
# Create: 2020-11-26

path=$(
  cd "$(dirname "$0")"
  pwd
)

systemctl stop firewalld

echo "install nginx"
yum install nginx gnutls gnutls-devel libev libev-devel -y

echo "start nginx"
if [ -f /run/nginx.pid ]; then
  /usr/sbin/nginx -s stop
  sleep 2
fi
/usr/sbin/nginx -c /etc/nginx/nginx.conf

echo "install nginx benchmark"
if [ ! -f /usr/bin/httpress ]; then
  rm -rf httpress
  git clone https://github.com/yarosla/httpress.git
  cd httpress && make
  cp bin/Release/httpress /usr/bin
fi

echo "update the nginx client"
sed -i "s#sh .*/nginx_benchmark.sh#sh $path/nginx_benchmark.sh#g" $path/nginx_client.yaml
sed -i "s#sh .*/nginx_benchmark.sh#sh $path/nginx_benchmark.sh#g" $path/nginx_http_long_client.yaml
