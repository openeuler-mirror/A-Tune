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
clustername=$1
tidbversion=$2
ip=$3
sed -i "s/- host:.*/- host: ${ip}/g" topo.yaml
echo "vm.swappiness = 0">> /etc/sysctl.conf
swapoff -a && swapon -a
sysctl -p
sudo systemctl stop firewalld.service
sleep 2
sudo systemctl disable firewalld.service
sleep 2
ntpstat
yum install -p ntp ntpdate && \
systemctl start ntpd.service && \
systemctl enable ntpd.service
sleep 5

curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh

source ~/.bash_profile

tiup update --self && tiup update cluster

tiup cluster deploy $clustername $tidbversion ./topo.yaml --user root -p

yum -y install mysql

ln -s /usr/local/mysql/bin/mysql /usr/bin
