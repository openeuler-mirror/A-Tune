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
# Create: 2020-12-03

if [ "$#" -ne 1 ]; then
  echo "USAGE: $0 warehouses"
  exit 1
fi

warehouses=$1

path=$(
  cd "$(dirname "$0")"
  pwd
)

echo "install mariadb"
yum install mariadb mariadb-server mariadb-devel -y
cp /etc/my.cnf /etc/my-tmp.cnf
cp my.cnf /etc/
systemctl restart mariadb

echo "update the mariadb client"
sed -i "s#sh .*/mariadb_benchmark.sh#sh $path/mariadb_benchmark.sh#g" "$path"/mariadb_client.yaml
sed -i "s#warehouses#$warehouses#g" "$path"/mariadb_benchmark.sh

echo "install mariadb benchmark"
rm -rf tpcc-mysql
git clone https://github.com/Percona-Lab/tpcc-mysql.git
cd tpcc-mysql/src && make
cd ..
cp tpcc_start /usr/bin

echo "create database and tables"
mysqladmin -u root -f drop tpcctest 2 &>/dev/null
mysql -u root -e "create database tpcctest"
mysql -u root tpcctest <create_table.sql
mysql -u root tpcctest <add_fkey_idx.sql
sed -i "s/STEP=.*/STEP=10/g" load.sh
sh load.sh tpcctest "$warehouses"
ret=0
while (($ret == 0)); do
  echo "loading data, please waiting ..."
  sleep 5
  ps -ef | grep tpcc_load | grep -v grep >/dev/null
  ret=$?
done
echo "loading data end"
