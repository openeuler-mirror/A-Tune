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
    print(status, file_name)
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
    if request.method == 'DELETE':
        remove_book(book_id)
        response_object['message'] = 'Book removed!'
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


def get_file_list(file_type, res):
    """get file list by type"""
    path = '/var/atune_data/tuning/' + file_type
    filelist = os.listdir(path)
    for each in filelist:
        filepath = path + '/' + each
        modify = os.path.getmtime(filepath)
        times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modify))
        current = {'name': each.split('.')[0], 'status': file_type, 'date': times}
        res.append(current)
    return res, len(filelist)



if __name__ == '__main__':
    config = ConfigParser()
    config.read('/etc/atuned/engine.cnf')
    app.run(host=config.get("server", "engine_host"), port='5000')

