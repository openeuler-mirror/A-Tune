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
# Create: 2022-6-25

"""
Routers for /v1/UI/analysis url.
"""

import logging
import json
from flask import abort
from flask_restful import Resource

from analysis.ui.parser import UI_ANALYSIS_GET_PARSER
from analysis.ui.config import UiConfig
from analysis.engine import transfer_web

LOGGER = logging.getLogger(__name__)
CORS = [('Access-Control-Allow-Origin', '*')]


class UiAnalysis(Resource):
    """restful api for web ui analysis page"""

    def get(self, cmd):
        """restful api get"""
        if not cmd:
            abort(404, 'does not get command')

        args = UI_ANALYSIS_GET_PARSER.parse_args()
        if not UiConfig.db_enable:
            if cmd == 'initialPage':
                return transfer_web.get_analysis_list()

            if cmd == 'rename':
                name = args.get('name')
                new_name = args.get('newName')
                return transfer_web.rename_analysis_file(name, new_name)

            if cmd == 'chooseFile':
                name = args.get('name')
                return json.dumps({'isExist': transfer_web.analysis_exist(name)}), 200, CORS

            if cmd == 'getAnalysisData':
                name = args.get('name')
                csv_line = int(args.get('csvLine'))
                log_line = int(args.get('logLine'))
                if not transfer_web.analysis_exist(name):
                    return json.dumps({'isExist': False}), 200, CORS
                return json.dumps(transfer_web.get_analysis_details(name, csv_line, log_line)), \
                        200, CORS

            if cmd == 'compareWith':
                name = args.get('name')
                line = int(args.get('csvLine'))
                if not transfer_web.analysis_exist(name):
                    return json.dumps({'isExist': False}), 200, CORS
                return json.dumps(transfer_web.get_analysis_details(name, line, -1)), 200, CORS
            return '', 200, CORS

        from analysis.ui.database import trigger_analysis
        if cmd == 'initialPage':
            uid = args.get('uid')
            res = trigger_analysis.get_analysis_list(int(uid))
            return json.dumps({'analysis': res}), 200, CORS

        if cmd == 'rename':
            name = args.get('name')
            new_name = args.get('newName')
            res, reason = trigger_analysis.rename_collection(name, new_name)
            return json.dumps({'rename': res, 'reason': reason}), 200, CORS

        if cmd == 'chooseFile':
            name = args.get('name')
            res = trigger_analysis.collection_exist(name)
            return json.dumps({'isExist': res}), 200, CORS

        if cmd == 'compareWith':
            name = args.get('name')
            line = args.get('csvLine')
            response_obj = trigger_analysis.get_compare_collection(name, int(line))
            return json.dumps(response_obj), 200, CORS

        if cmd == 'getAnalysisData':
            name = args.get('name')
            csv_line = args.get('csvLine')
            log_line = args.get('logLine')
            response_obj = trigger_analysis.get_analysis_data(name, int(csv_line), int(log_line))
            return json.dumps(response_obj), 200, CORS
        return '', 200, CORS
