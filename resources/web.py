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
import time
import numpy
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from configparser import ConfigParser


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app)


@app.route('/tuning/<status>/<file_name>', methods=['GET'])
def get_file_info(status, file_name):
    """get tuning info"""
    response_object = {}
    response_object['status'] = status
    response_object['file_name'] = file_name
    path = '/var/atune_data/tuning/' + status + '/' + file_name + '.txt'
    if not os.path.exists(path):
        response_object['find_file'] = False
        return jsonify(response_object)
    params = []
    with open(path, 'r') as tuning_file:
        infos = tuning_file.readline()[:-1].split(',')
        base = tuning_file.readline()[:-1]
        params = tuning_file.readline()[:-1].split(',')
    response_object['engine'] = infos[0]
    response_object['round'] = infos[1]
    response_object['find_file'] = True
    response_object['parameter'] = params
    response_object['line'] = 0
    response_object['base'] = base
    return jsonify(response_object)


@app.route('/tuning/<status>/<file_name>/<line>', methods=['GET'])
def get_file_data(status, file_name, line):
    """get tuning data"""
    line = int(line)
    response_object = {}
    response_object['status'] = status
    response_object['file_name'] = file_name
    response_object['initial_line'] = line
    path = '/var/atune_data/tuning/' + status + '/' + file_name + '.txt'
    if not os.path.exists(path):
        response_object['find_file'] = False
        return jsonify(response_object)
    res = []
    cost = []
    count = 0
    params = []
    eof = False
    with open(path, 'r') as tuning_file:
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
            res.append(line_list[1].split(','))
            count += 1
            if count == 10:
                break
    res = numpy.array(res).T.tolist()
    line_res = line + count
    if eof:
        line_res = -1
    response_object['find_file'] = True
    response_object['parameter'] = params
    response_object['line'] = line_res
    response_object['data'] = res
    response_object['cost'] = cost
    return jsonify(response_object)


@app.route('/tuning/<types>', methods=['GET'])
def get_type_list(types):
    """get type list"""
    res = []
    finished = 0
    running = 0
    error = 0
    path = '/var/atune_data/tuning/'
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(path + '/running'):
        os.makedirs(path + '/running')
    if not os.path.exists(path + '/finished'):
        os.makedirs(path + '/finished')
    if not os.path.exists(path + '/error'):
        os.makedirs(path + '/error')

    if types == 'all':
        res, _ = get_file_list('running', res)
        res, _ = get_file_list('finished', res)
        res, _ = get_file_list('error', res)
    else:
        res, _ = get_file_list(types, res)

    if len(res) > 0:
        res = sorted(res, key=(lambda x:x['date']), reverse=True)
    response_object = {}

    if request.method == 'GET':
        response_object['message'] = res
    return jsonify(response_object)


@app.route('/tuning/findFile/<filename>', methods=['GET'])
def find_file_dir(filename):
    """find file by name"""
    response_object = {}
    response_object['status'] = 'running'
    path = '/var/atune_data/tuning/'
    filename += '.txt'
    if os.path.exists(path + 'finished/' + filename):
        response_object['status'] = 'finished'
    elif os.path.exists(path + 'error/' + filename):
        response_object['status'] = 'error'
    return jsonify(response_object)


@app.route('/analysis', methods=['GET'])
def get_analysis_list():
    """get analysis file list"""
    response_object = {}
    path = '/var/atune_data/analysis'
    res = []
    filelist = os.listdir(path)
    for each in filelist:
        if each.endswith('.csv'):
            filename = each.rsplit('.')[0]
            if filename not in res:
                filepath = path + '/' + each
                modify = os.path.getmtime(filepath)
                times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modify))
                temp = {'name': filename, 'date': times}
                res.append(temp)
    res = sorted(res, key=(lambda x:x['date']), reverse=True)
    response_object['analysis'] = res
    return jsonify(response_object)


@app.route('/analysis/<filename>/<line>', methods=['GET'])
def get_analysis_details(filename, line):
    """get analysis info details"""
    line = int(line)
    response_object = {'line': line + 20}
    path = '/var/atune_data/analysis/' + filename
    if not os.path.exists(path + ".csv"):
        response_object['file_exist'] = False
        return jsonify(response_object)
    response_object['file_exist'] = True
    csv_res, csv_count, table_header = get_analysis_csv(path + ".csv", line)
    csv_res = numpy.array(csv_res).T.tolist()
    response_object['csv_data'] = csv_res
    response_object['csv_lines'] = csv_count
    response_object['table_header'] = table_header
    if not os.path.exists(path + ".log"):
        response_object['log_data'] = []
        response_object['log_lines'] = 0
        return jsonify(response_object)
    log_res = []
    log_count = 0
    with open(path + ".log", 'r') as analysis_log:
        workload = analysis_log.readline()[:-1]
        lines = analysis_log.readlines()
        while line + log_count < len(lines):
            log_res.append(lines[line + log_count][:-1].split("|"))
            log_count += 1
            if log_count == 20:
                break
    response_object['workload'] = workload
    response_object['log_data'] = log_res
    response_object['log_lines'] = log_count
    return jsonify(response_object)


def get_analysis_csv(path, line):
    """get analysis csv"""
    count = 0
    res = []
    with open(path, 'r') as analysis_file:
        table_header = analysis_file.readline()[:-1].split(',')
        lines = analysis_file.readlines()
        while line + count < len(lines):
            line_list = lines[line + count][:-1].split(',')
            res.append(line_list)
            count += 1
            if count == 20:
                break
        return res, count, table_header


def get_file_list(file_type, res):
    """get file list by type"""
    path = '/var/atune_data/tuning/' + file_type
    filelist = os.listdir(path)
    for each in filelist:
        filepath = path + '/' + each
        modify = os.path.getmtime(filepath)
        times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modify))
        current = {'name': each.rsplit('.', 1)[0], 'status': file_type, 'date': times}
        res.append(current)
    return res, len(filelist)


if __name__ == '__main__':
    config = ConfigParser()
    config.read('/etc/atuned/engine.cnf')
    app.run(host=config.get("server", "engine_host"), port='5000')

