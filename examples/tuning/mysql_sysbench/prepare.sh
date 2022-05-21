#!/bin/sh
# Copyright (c) lingff(ling@stu.pku.edu.cn),
# School of Software & Microelectronics, Peking University.
#
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
#
# Create: 2021-05-24

path=$(
  cd "$(dirname "$0")"
  pwd
)

installation="mysql"
sysbench_cfg="--with-mysql-libs=/usr/local/mysql/lib/ --with-mysql-includes=/usr/local/mysql/include/"
cmd_service_link="ln -s /usr/local/mysql/support-files/mysql.server /etc/init.d/mysql"
cmd_add_path="export PATH=`echo $PATH`:/usr/local/mysql/bin"

version=`cat /etc/system-release`
if [[ "$version" != *"20.03"* ]]; then
    installation="$installation mysql-devel mysql-server"
    sysbench_cfg=""
    cmd_service_link=""
    cmd_add_path=""
fi


echo "install MySQL..."
yum install -y $installation
rm -rf /etc/init.d/mysql
eval $cmd_service_link
mkdir -p /usr/local/mysql/{data,tmp,run,log}
chown -R mysql:mysql /usr/local/mysql


echo "initializing MySQL..."
rm -rf /etc/my.cnf
cp my.cnf /etc
kill -9 `pidof mysqld`
rm -rf /usr/local/mysql/data/*
eval $add_path
mysqld --user=root --initialize-insecure


echo "start MySQL..."
if [[ "$version" != *"20.03"* ]]; then
    taskset -c 0,1 mysqld --user=root &
    sleep 5
    rm -rf /var/lib/mysql/mysql.sock
    ln -s /tmp/mysql.sock /var/lib/mysql/mysql.sock
else
    systemctl daemon-reload
    taskset -c 0,1 systemctl restart mysql
fi


echo "create database..."
mysql -uroot << EOF
alter user 'root'@'localhost' identified by '123456';
flush privileges;
use mysql;
update user set host='%' where user='root';
flush privileges;
create database sbtest;
quit
EOF


echo "install sysbench..."
yum install -y git
git clone --depth=1 https://github.com/akopytov/sysbench.git
cd sysbench
yum install -y automake libtool
./autogen.sh
./configure $sysbench_cfg
make -j
make install


echo "checking sysbench..."
sysbench --version
if [ $? -ne 0 ]; then   
    echo "sysbench FAILED";   
    exit 1;   
fi


echo "update the client and server yaml files"
sed -i "s#sh .*/mysql_sysbench_benchmark.sh#sh $path/mysql_sysbench_benchmark.sh#g" $path/mysql_sysbench_client.yaml
sed -i "s#cat .*/sysbench_oltp_read_write.log#cat $path/sysbench_oltp_read_write.log#g" $path/mysql_sysbench_client.yaml
if [[ "$version" != *"20.03"* ]]; then
    sed -i "s#startworkload:.*#startworkload: \"\`mysqld \& \` \& sleep 10\" #g" $path/mysql_sysbench_server.yaml
    sed -i "s#stopworkload:.*#stopworkload: \"mysqladmin -S/var/lib/mysql/mysql.sock shutdown -uroot -p123456\" #g" $path/mysql_sysbench_server.yaml
else
    sed -i "s#startworkload:.*#startworkload: \"taskset -c 0,1 systemctl start mysql\" #g" $path/mysql_sysbench_server.yaml
    sed -i "s#stopworkload:.*#stopworkload: \"systemctl stop mysql\" #g" $path/mysql_sysbench_server.yaml
fi


echo "copy the server yaml file to /etc/atuned/tuning/"
cp $path/mysql_sysbench_server.yaml /etc/atuned/tuning/
