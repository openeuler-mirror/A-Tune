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
# Create: 2022-7-30

"""
Routers for /v2/UI/offline url
"""

import logging
import json
from flask import abort
from flask_restful import Resource

from analysis.ui.parser import UI_TUNING_GET_PARSER
from analysis.ui.config import UiConfig
from analysis.engine import transfer_web

LOGGER = logging.getLogger(__name__)
CORS = [('Access-Control-Allow-Origin', '*')]


class OfflineTunning(Resource):
    """restful api for web ui offline page"""

    def get(self, cmd):
        """restful apu get"""
        if not cmd:
            abort(404, 'does not get command')

        args = UI_TUNING_GET_PARSER.parse_args()
        if not UiConfig.db_enable:
            if cmd == 'getData':
                name = args.get('name')
                status = args.get('status')
                line = args.get('line')
                response_obj = {}
                response_obj['status'] = status
                if not transfer_web.tuning_exist(status, name):
                    response_obj['isExist'] = False
                    return json.dumps(response_obj), 200, CORS
                return json.dumps(transfer_web.get_file_data(status, name, line,
                                                             response_obj)), 200, CORS

            if cmd == 'getTuningStatus':
                name = args.get('name')
                return json.dumps(transfer_web.find_file_dir(name)), 200, CORS
            return '', 200, CORS

        from analysis.ui.database import trigger_tuning
        if cmd == 'getData':
            name = args.get('name')
            status = args.get('status')
            line = args.get('line')
            response_obj = trigger_tuning.get_tuning_data(status, name, line)
            return json.dumps(response_obj), 200, CORS

        if cmd == 'getTuningStatus':
            name = args.get('name')
            res = trigger_tuning.get_tuning_status(name)
            return json.dumps({'status': res}), 200, CORS
        return '', 200, CORS
