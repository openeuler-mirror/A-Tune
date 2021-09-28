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
path=$(
  cd "$(dirname "$0")"
  pwd
)

# These variables will be assigned when running 'sh prepare.sh'
local_memcached_ip=
memaslap_ip=

# benchmark
ssh -t root@$memaslap_ip "/usr/local/libmemcached/bin/memaslap -s $local_memcached_ip:11211 -T 4 -c 768 -t 30s > memaslap_benchmark.log ; scp memaslap_benchmark.log root@$local_memcached_ip:$path"