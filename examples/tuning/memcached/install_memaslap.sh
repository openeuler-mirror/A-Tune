#!/bin/sh
# Copyright (c) lixi(xili@std.uestc.edu.cn),
# School of Information and Software Engineering, University of Electronic Science and Technology of China.
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
# Create: 2021-09-29
echo "install telnet..."
yum install telnet gcc-c++ -y

echo "close firewalld..."
systemctl stop firewalld
systemctl disable firewalld
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux

echo "install libevent..."
yum install libevent libevent-devel -y

echo "download and install libmemcached..."
wget https://launchpad.net/libmemcached/1.0/1.0.18/+download/libmemcached-1.0.18.tar.gz
tar -zxvf libmemcached-1.0.18.tar.gz
cd libmemcached-1.0.18

./configure -prefix=/usr/local/libmemcached --with-memcached --enable-memaslap

echo "fix install bugs(when gcc --version > 7)..."
sed -i 's/if (opt_servers == false)/if (opt_servers == NULL)/g' ./clients/memflush.cc
sed -i '2937c LDFLAGS = -L/lib64 -lpthread' ./Makefile
if [[ -n "`gcc --version | awk '/gcc/ && ($3+0)>=10 {print 1}'`" ]]; then
	sed -i 's/^CFLAGS = /CFLAGS = -fcommon /g' ./Makefile
fi

make
make install

echo "installed memasalp..."
