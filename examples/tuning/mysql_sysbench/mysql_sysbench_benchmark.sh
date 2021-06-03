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


sysbench --config-file=sysbench_config.cfg oltp_read_write --tables=10 --table-size=200000 --time=30 prepare
taskset -c 2,3 sysbench --config-file=sysbench_config.cfg oltp_read_write --tables=10 --table-size=200000 --time=300 --mysql-ignore-errors=8005 run  > sysbench_oltp_read_write.log
sysbench --config-file=sysbench_config.cfg oltp_read_write --tables=10 --table-size=200000 --time=300 --mysql-ignore-errors=8005 cleanup