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

import re
import datetime
import shutil
import logging
import tarfile
import pandas as pd
from pathlib import Path

from analysis.default_config import TUNING_DATA_PATH, TUNING_DATA_DIRS


def read_from_csv(path):
    """read data from csv"""
    if not Path(path).exists():
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
    path = TUNING_DATA_PATH + "running/"
    if not Path(path).exists():
        create_dir()
    path = path + filename + ".txt"
    with open(path, mode) as file_handle:
        file_handle.write(str(data))
        file_handle.write("\n")
        file_handle.close()


def create_dir():
    """create dir if not exist"""
    for dir_name in TUNING_DATA_DIRS:
        Path(TUNING_DATA_PATH + dir_name).mkdir(parents=True, exist_ok=True)


def change_file_name(filename, dest):
    """change tuning file name"""
    path = TUNING_DATA_PATH + "running/"
    dir_path = TUNING_DATA_PATH + dest + "/"
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    shutil.move(path + filename + ".txt", dir_path + filename + ".txt")


def get_time_difference(end_time, start_time):
    """get time difference in second"""
    end_time += "000"
    start_time += "000"
    end = [int(ele) for ele in re.split(r"-| |:|\.", end_time)]
    start = [int(ele) for ele in re.split(r"-| |:|\.", start_time)]
    date_end = datetime.datetime(end[0], end[1], end[2], end[3], end[4], end[5], end[6])
    date_start = datetime.datetime(start[0], start[1], start[2],
                                   start[3], start[4], start[5], start[6])
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


def zip_key_value(key, val_array):
    """zip key and value together"""
    res = []
    for line in val_array:
        res.append(dict(zip(key, line)))
    return res
