#!/usr/bin/bash

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
# @Author    :   westtide
# @Contact   :   tocokeo@outlook.com
# @Date      :   2023/9/22
# @License   :   Mulan PSL v2
# @Desc      :   clean data files in /data directory
# #############################################

import os


# clan_data: 用于清理 /data 目录下的文件：交叉对比参数的临时文件、统计结果
def clean_files_with_prefix(directory, prefix):
    for filename in os.listdir(directory):
        if filename.startswith(prefix) and filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
                print(f"文件 {filename} 已成功删除")
            except OSError as e:
                print(f"删除文件 {filename} 时出现错误：{e}")


data_directory = "./data/"
prefix_to_clean = ["differ-2023", "statistical-2023", "backup_", "sysctl", "ulimit"]

for prefix in prefix_to_clean:
    clean_files_with_prefix(data_directory, prefix)
