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
# Create: 2020-08-17

"""
Web UI initialization
"""


import os
import json
import time
import numpy

from analysis.engine.config import EngineConfig
from analysis.engine.utils import utils
from analysis.default_config import ANALYSIS_DATA_PATH, TUNING_DATA_PATH

CORS = [('Access-Control-Allow-Origin', '*')]


def tuning_exist(status, file_name):
    """check if tuning file exist"""
    path = TUNING_DATA_PATH + status + '/' + file_name + '.txt'
    return os.path.exists(path)


def get_file_info(status, file_name):
    """get tuning info"""
    response_object = {}
    response_object['status'] = status
    response_object['file_name'] = file_name
    path = TUNING_DATA_PATH + status + '/' + file_name + '.txt'
    params = []
    with open(path, 'r', encoding='utf-8') as tuning_file:
        infos = tuning_file.readline()[:-1].split(',')
        base = tuning_file.readline()[:-1]
        params = tuning_file.readline()[:-1].split(',')
    response_object['engine'] = infos[0]
    response_object['round'] = infos[1]
    response_object['isExist'] = True
    response_object['parameter'] = params
    response_object['line'] = 0
    response_object['base'] = base
    return response_object


def rename_tuning_file(file_name, new_name):
    """rename tuning file"""
    locate = TUNING_DATA_PATH + 'finished/'
    old_path = locate + file_name + '.txt'
    new_path = locate + new_name + '.txt'
    response_object = rename_file(old_path, new_path)
    return json.dumps(response_object), 200, CORS


def get_file_data(status, file_name, line, response_object):
    """get tuning data"""
    line = int(line)
    response_object['file_name'] = file_name
    response_object['initial_line'] = line
    path = TUNING_DATA_PATH + status + '/' + file_name + '.txt'
    res = []
    cost = []
    count = 0
    params = []
    eof = False
    with open(path, 'r', encoding='utf-8') as tuning_file:
        _ = tuning_file.readline()
        _ = tuning_file.readline()
        params = tuning_file.readline()[:-1].split(',')
        lines = tuning_file.readlines()
        while line + count < len(lines):
            if lines[line + count][:-1] == 'END' or lines[line + count][:-1] == 'ERROR':
                eof = True
                break
            line_list = lines[line + count][:-1].split(',', 1)
            cost.append(line_list[0])
            temp_line = line_list[1].split(',')
            temp_line.insert(0, str(line + count + 1))
            res.append(temp_line)
            count += 1
            if count == 10:
                break
    res = numpy.array(res).T.tolist()
    line_res = line + count
    if eof:
        line_res = -1
    response_object['isExist'] = True
    response_object['parameter'] = params
    response_object['line'] = line_res
    response_object['data'] = res
    response_object['cost'] = cost
    return response_object


def get_type_list(types):
    """get type list"""
    res = []
    utils.create_dir()

    if types == 'all':
        res, _ = get_file_list('running', res)
        res, _ = get_file_list('finished', res)
        res, _ = get_file_list('error', res)
    else:
        res, _ = get_file_list(types, res)

    if len(res) > 0:
        res = sorted(res, key=(lambda x:x['date']), reverse=True)
    response_object = {}
    response_object['message'] = res
    return json.dumps({'message': res}), 200, CORS


def find_file_dir(filename):
    """find file by name"""
    response_object = {}
    response_object['status'] = 'running'
    filename += '.txt'
    if os.path.exists(TUNING_DATA_PATH + 'finished/' + filename):
        response_object['status'] = 'finished'
    elif os.path.exists(TUNING_DATA_PATH + 'error/' + filename):
        response_object['status'] = 'error'
    else:
        response_object['status'] = 'unknown'
    return response_object


def get_analysis_list():
    """get analysis file list"""
    response_object = {}
    res = []
    filelist = os.listdir(ANALYSIS_DATA_PATH)
    for each in filelist:
        if each.endswith('.csv'):
            filename = each.rsplit('.')[0]
            if filename not in res:
                filepath = ANALYSIS_DATA_PATH + each
                modify = os.path.getmtime(filepath)
                times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modify))
                temp = {'name': filename, 'status': 'finished', 'date': times,
                        'info': EngineConfig.engine_host}
                res.append(temp)
    res = sorted(res, key=(lambda x:x['date']), reverse=True)
    response_object['analysis'] = res
    return json.dumps(response_object), 200, CORS


def rename_analysis_file(file_name, new_name):
    """rename tuning file"""
    old_path = ANALYSIS_DATA_PATH + file_name
    new_path = ANALYSIS_DATA_PATH + new_name
    response_object = rename_file(old_path + '.csv', new_path + '.csv')
    rename_file(old_path + '.log', new_path + '.log')
    return json.dumps(response_object), 200, CORS


def analysis_exist(file_name):
    """check if analysis file exist"""
    path = ANALYSIS_DATA_PATH + file_name
    return os.path.exists(path + ".csv")


def get_analysis_details(file_name, csv_line, log_line):
    """get analysis info details"""
    path = ANALYSIS_DATA_PATH + file_name
    response_object = {}
    response_object['isExist'] = True
    csv_res, csv_count, table_header = get_analysis_csv(path + ".csv", csv_line)
    csv_res = numpy.array(csv_res).T.tolist()
    if csv_count == 0 or csv_count % 5 != 0:
        response_object['hasNext'] = False
    else:
        response_object['hasNext'] = True
        response_object['interval'] = 0
    response_object['csv_data'] = csv_res
    response_object['nextCsv'] = csv_count + csv_line
    response_object['table_header'] = table_header
    if not os.path.exists(path + ".log") or log_line == -1:
        response_object['log_data'] = []
        response_object['nextLog'] = log_line
        return response_object
    log_res = []
    log_count = 0
    with open(path + ".log", 'r', encoding='utf-8') as analysis_log:
        workload = analysis_log.readline()[:-1]
        lines = analysis_log.readlines()
        while log_line + log_count < len(lines):
            log_res.append(lines[log_line + log_count][:-1].split("|"))
            log_count += 1
            if log_count == 5:
                break
    response_object['workload'] = workload
    response_object['log_data'] = log_res
    response_object['nextLog'] = log_count + log_line
    return response_object


def rename_file(old_path, new_path):
    """rename helper function"""
    response_object = {}
    if os.path.isfile(old_path):
        if not os.path.isfile(new_path):
            os.rename(old_path, new_path)
            response_object['rename'] = True
        else:
            response_object['reason'] = 'duplicate'
            response_object['rename'] = False
    else:
        response_object['reason'] = 'error'
        response_object['rename'] = False
    return response_object


def get_analysis_csv(path, line):
    """get analysis csv"""
    count = 0
    res = []
    with open(path, 'r', encoding='utf-8') as analysis_file:
        table_header = analysis_file.readline()[:-1].split(',')
        lines = analysis_file.readlines()
        while line + count < len(lines):
            line_list = lines[line + count][:-1].split(',')
            res.append(line_list)
            count += 1
            if count == 5:
                break
        return res, count, table_header


def get_file_list(file_type, res):
    """get file list by type"""
    path = TUNING_DATA_PATH + file_type
    filelist = os.listdir(path)
    for each in filelist:
        filepath = path + '/' + each
        modify = os.path.getmtime(filepath)
        times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modify))
        current = {'name': each.rsplit('.', 1)[0], 'status': file_type, 'date': times,
                   'info': EngineConfig.engine_host}
        res.append(current)
    return res, len(filelist)
