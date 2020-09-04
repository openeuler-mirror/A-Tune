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
import numpy
import logging
from flask import Flask, render_template
from flask_socketio import SocketIO
from configparser import ConfigParser


APP = Flask(__name__, template_folder='./templates', static_folder='./static')
APP.config['TEMPLATES_AUTO_RELOAD'] = True
APP.jinja_env.auto_reload = True
socketio = SocketIO(APP, async_mode=None)


@APP.route('/tuning')
def index():
    """open tuning page"""
    return render_template('tuning.html', async_mode=socketio.async_mode)


@socketio.on('connect', namespace='/tuning')
def init_connect():
    """inital connection"""
    return


@socketio.on('show_page', namespace='/tuning')
def show_page(timestamp, _):
    """list all tuning project name on page"""
    path = '/etc/atuned/webserver'
    filelist = os.listdir(path)
    filelist.sort(key=lambda fn: os.path.getmtime(path + '/' + fn), reverse=True)
    res = []
    for each in filelist:
        res.append(each.split('.')[0])
    socketio.emit('get_all_tuning_list', {'prj_list': res, 'timestamp': timestamp}, namespace='/tuning')
    return


@socketio.on('inital_chart', namespace='/tuning')
def inital_tuning_page(message, timestamp, _):
    """inital chart graph for project"""
    prj_name = message['prj_name']
    path = '/etc/atuned/webserver/' + prj_name + '.txt'
    if not os.path.exists(path):
        socketio.emit('file_removed', {'prj_name': prj_name, 'timestamp': timestamp}, namespace='/tuning')
        return
    graph_list = []
    with open(path, 'r') as tuning_file:
        graph_list = tuning_file.readline()[:-1].split(',')
    socketio.emit('inital_chart',
                  {'graph_list': graph_list, 'prj_name': prj_name, 'timestamp': timestamp},
                  namespace='/tuning')


@socketio.on('update_chart', namespace='/tuning')
def update_tuning_page(prj_name, num, timestamp, _):
    """get info for chart"""
    path = '/etc/atuned/webserver/' + prj_name + '.txt'
    if not os.path.exists(path):
        socketio.emit('file_removed', {'prj_name': prj_name, 'timestamp': timestamp}, namespace='/tuning')
        return
    res = []
    count = 0
    first_line = ''
    eof = False
    with open(path, 'r') as tuning_file:
        first_line = tuning_file.readline()[:-1].split(',')
        lines = tuning_file.readlines()
        while num + count < len(lines):
            if lines[num + count][:-1] == 'END':
                eof = True
                break
            line_list = lines[num + count][:-1].split(',')
            res.append(line_list)
            count += 1
            if count == 5:
                break
    res = numpy.array(res).T.tolist()
    next_line = num + count
    if eof:
        next_line = -1
    socketio.emit('update_chart',
                  {'name': first_line, 'num': num, 'next_line': next_line, 'value': res, 'timestamp': timestamp},
                  namespace='/tuning')


if __name__ == '__main__':
    config = ConfigParser()
    config.read('/etc/atuned/engine.cnf')
    socketio.run(APP, host=config.get("server", "engine_host"), port=10086)
