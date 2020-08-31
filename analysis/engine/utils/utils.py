#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-10-29

"""
Provide an interface to read data from csv.
"""

import os
import re
import time
import random
import logging
import tarfile
import pandas as pd


def read_from_csv(path):
    """read data from csv"""
    if not os.path.exists(path):
        return None
    if not path.endswith('.csv'):
        return None

    with open(path, 'r') as file:
        data = pd.read_csv(file, header=0)

    return data


def extract_file(file_path, target_path):
    """extract file"""
    tar = tarfile.open(file_path)
    logging.debug("%s", tar.getnames())
    tar.extractall(path=target_path)
    tar.close()
    res_path = file_path.rpartition('-')[0]
    return res_path


def add_data_to_file(data, mode, filename):
    """write tuning result to file"""
    path = "/etc/atuned/webserver/" + filename + ".txt"
    file_handle = open(path, mode)
    file_handle.write(str(data))
    file_handle.write("\n")
    file_handle.close()


def change_file_name():
    """change tuning file name"""
    path = "/etc/atuned/webserver/"
    file_list = os.listdir(path)
    file_list.sort(key=lambda fn: os.path.getmtime(path + fn))
    if len(file_list) > 0 and re.match(r'\S*-\d{17}\S*', file_list[-1]) is None:
        old_name = file_list[-1].split(".")[0]
        curr_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        new_name = old_name + "-" + str(curr_time) + str(random.randint(100, 999))
        os.rename(path + old_name + ".txt", path + new_name + ".txt")
