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
# Create: 2020-12-17

"""
Routers for /v1/UI/tuning url.
"""

import logging
import json
from flask import abort
from flask_restful import Resource

from analysis.engine.parser import UI_USER_GET_PARSER
from analysis.engine.database import trigger_user

LOGGER = logging.getLogger(__name__)
CORS = [('Access-Control-Allow-Origin', '*')]


class UiUser(Resource):
    """restful api for web ui user login/profile page"""

    def get(self, cmd):
        """restful api get"""
        if not cmd:
            abort(404, 'does not get command')

        args = UI_USER_GET_PARSER.parse_args()
        if cmd == 'login':
            email = args.get('email')
            pwd = args.get('password')
            res, name = trigger_user.user_exist(email, pwd)
            if res == -1:
                return json.dumps({'login': False}), 200, CORS
            return json.dumps({'login': True, 'user_id': res, 'user_name': name}), 200, CORS

        if cmd == 'signup':
            email = args.get('email')
            pwd = args.get('password')
            name = args.get('name')
            res, dup = trigger_user.create_user(email, pwd, name)
            if res:
                return json.dumps({'signup': res}), 200, CORS
            return json.dumps({'signup': res, 'duplicate': dup}), 200, CORS

        return '', 200, CORS
