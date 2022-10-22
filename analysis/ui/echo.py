#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2022-9-20

"""
Routers for /v2/UI/echo url
"""

from cmath import pi
import logging
import json
from flask import abort, request
from flask_restful import Resource
from socket import *

from analysis.atuned.utils.npipe import NPipe, get_npipe

LOGGER = logging.getLogger(__name__)
CORS = [('Access-Control-Allow-Origin', '*')]


class EchoTunning(Resource):
    """restful api for web ui echo"""

    def post(self):
        """restful apu get"""
        tuning_command = 'atune-adm '
        if request.json == None:
            return abort(404, 'does not get body')
        tuning_command = tuning_command + request.json['command']
        print(request.json['options'])
        for option in request.json['options']:
            tuning_command = tuning_command + ' ' + \
                option['option'] + ' '+option['value']
        tuning_command = tuning_command + ' ' + request.json['yaml']
        pipe = NPipe()
        res=pipe.open()
        pipe.write(tuning_command)
        pipe.close()
        return res, 200, CORS

    def get(self):
        IP = ''
        PORT = 5002
        BUFFER_SIZE = 512
        listenSocket = socket(AF_INET, SOCK_STREAM)
        listenSocket.bind((IP, PORT))
        listenSocket.listen(8)
        dataSocket, addr = listenSocket.accept()
        n_pipe = get_npipe(args.get("session_id"))
        while True:
            echo = n_pipe.get()
            if echo:
                break
            dataSocket.send(echo)
        dataSocket.close()
        listenSocket.close()