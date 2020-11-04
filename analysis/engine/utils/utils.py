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
import datetime
import random
import shutil
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
    path = "/var/atune_data/tuning/running/"
    if not os.path.exists(path):
        create_dir()
    path = path + filename + ".txt"
    with open(path, mode) as file_handle:
        file_handle.write(str(data))
        file_handle.write("\n")
        file_handle.close()


def create_dir():
    """create dir if not exist"""
    path = "/var/atune_data/"
    if not os.path.exists(path):
        os.makedirs(path)
    path += "tuning/"
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(path + "/running"):
        os.makedirs(path + "/running")
    if not os.path.exists(path + "/finished"):
        os.makedirs(path + "/finished")
    if not os.path.exists(path + "/error"):
        os.makedirs(path + "/error")


def change_file_name(filename, dest):
    """change tuning file name"""
    path = "/var/atune_data/tuning/running/"
    dir_path = "/var/atune_data/tuning/" + dest + "/"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    shutil.move(path + filename + ".txt", dir_path + filename + ".txt")


def get_time_difference(end_time, start_time):
    """get time difference in second"""
    end_time += "000"
    start_time += "000"
    end = re.split(r"-| |:|\.", end_time)
    start = re.split(r"-| |:|\.", start_time)
    for i in range(len(end)):
        end[i] = int(end[i])
        start[i] = int(start[i])
    date_end = datetime.datetime(end[0], end[1], end[2], end[3], end[4], end[5], end[6])
    date_start = datetime.datetime(start[0], start[1], start[2], start[3], start[4], start[5], start[6])
    return str((date_end - date_start).total_seconds())


def get_opposite_num(num, opposite):
    """get opposite number for string"""
    if num[0] == "-":
        return num[1:]
    if opposite and num[0] != "-":
        return "-" + num
    return num


def get_string_split(line, index, key, val):
    """get split value for line"""
    params = ""
    for element in line.split("|")[index].split(","):
        params += val + element.split("=")[key] + ","
    return params
