#!/usr/bin/python3

# Copyright (c) 2022 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   shangyingjie
# @Contact   :   yingjie@isrc.iscas.ac.cn
# @Date      :   2022/3/6
# @License   :   Mulan PSL v2
# @Desc      :   Redis benchmark script
# #############################################

import subprocess
import os


def get_output(cmd: str):
    """
    Return the result of executing a command.
    """
    output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return output.returncode, output.stdout


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    redis_server_ip = 'will be replaced after running prepare.sh'
    redis_server_port = 'will be replaced after running prepare.sh'
    retcode, stdoutput = get_output(
        f"redis-cli -h {redis_server_ip} -p {redis_server_port} ping")
    if retcode != 0:
        print("failed to access redis-server!")
        exit(1)
    else:
        print("access redis-server successfully.")

    print("start test...")
    retcode, benchmark_csv = get_output(
        f"redis-benchmark -h {redis_server_ip} -p {redis_server_port} -t set,get,incr,rpop,sadd,hset,lrange_600 --csv")

    total_queries = 0
    for line in benchmark_csv.splitlines():
        total_queries += float(line.split(',')[1].replace('"', ''))

    result = benchmark_csv + "\n" + f"total queries: {total_queries}"
    print(result)
    with open("redis_benchmark.log", "w") as f:
        f.write(result)
