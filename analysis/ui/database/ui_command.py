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
# Create: 2023-2-16

"""
Routers for /v1/UI/command url.
"""

import logging
import json
from flask import abort
from flask_restful import Resource

from analysis.ui.parser import UI_COMMAND_GET_PARSER
from analysis.ui.config import UiConfig
from analysis.engine import transfer_web
from analysis.ui.util import authenticate

LOGGER = logging.getLogger(__name__)
CORS = [('Access-Control-Allow-Origin', '*')]

class UiCommand(Resource):
    """restful api for web ui command page"""
    method_decorators = [authenticate]

    def get(self, cmd):
        """restful api get"""
        if not cmd:
            abort(404, 'does not get command')
        
        args = UI_COMMAND_GET_PARSER.parse_args()

        from analysis.ui.database import trigger_command
        if cmd == 'initialPage':
            uid = args.get('uid')
            res = trigger_command.count_command_list(int(uid))
            return json.dumps({'count': res}), 200, CORS
        
        if cmd == 'getList':
            uid = int(args.get('uid'))
            page_num = int(args.get('pageNum'))
            page_size = int(args.get('pageSize'))
            list = trigger_command.get_command_list(uid, page_num, page_size)
            return json.dumps({'data': list}), 200, CORS

        if cmd == 'updateDescription':
            cid = args.get('cid')
            description = args.get('description')
            res = trigger_command.update_command_description(cid, description)
            return json.dumps({'status': res}), 200, CORS