#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2022 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2022-06-25

"""
Routers for /v1/UI/role url.
"""

import logging
import json
from flask import abort
from flask_restful import Resource

from analysis.ui.parser import UI_ROLE_GET_PARSER
from analysis.ui.config import UiConfig
from analysis.ui.database import trigger_user

LOGGER = logging.getLogger(__name__)
CORS = [('Access-Control-Allow-Origin', '*')]


class UiRole(Resource):
    """Role restful API used for role management"""

    def get(self, cmd):
        """restful api get"""
        if not cmd:
            abort(404, 'does not get command')

        args = UI_ROLE_GET_PARSER.parse_args()
        if not UiConfig.db_enable:
            return json.dumps({'connectDB': False}), 200, CORS
        if cmd == 'initialPage':
            uid = args.get('userId')
            if uid == 1:
                return trigger_user.get_user_list()
            else:
                return json.dumps({'initialPage': False}), 200, CORS

        if cmd == 'deleteUser':
            uid = args.get('userId')
            res = trigger_user.delete_user(uid)
            return json.dumps({'initialPage': res}), 200, CORS

        if cmd == 'updateUser':
            uid = args.get('userId')
            pwd = args.get('password')
            name = args.get('name')
            role = args.get('role')
            res = trigger_user.update_user(uid, pwd, name, role)
            if res:
                return json.dumps({'initialPage': res}), 200, CORS
            return json.dumps({'updateUser': False}), 200, CORS
