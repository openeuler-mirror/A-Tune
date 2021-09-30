#!/bin/sh
# Copyright (c) liyang(innovation64feng@gmail.com),
# Information Management and Information System, Beijing University of Chinese Medicine.
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
# Create: 2021-09-30
wget https://github.com/akopytov/sysbench/archive/refs/tags/1.0.14.tar.gz
tar -zxvf 1.0.14.tar.gz
cd sysbench-1.0.14
./autogen.sh
sleep 10
./configure --with-mysql-includes=/usr/local/mysql/include --with-mysql-libs=/usr/local/mysql/lib
sleep 10
make && make install