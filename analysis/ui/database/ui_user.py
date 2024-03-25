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
Routers for /v1/UI/user url.
"""

import logging
import json
from flask import abort, request
from flask_restful import Resource

from analysis.ui.cache import LocalCache
from analysis.ui.parser import UI_USER_GET_PARSER, UI_USER_POST_PARSER
from analysis.ui.config import UiConfig
from analysis.ui.util import JwtUtil, verify_server_connectivity, decode_server_password, authenticate

LOGGER = logging.getLogger(__name__)
CORS = [('Access-Control-Allow-Origin', '*')]


class UiUser(Resource):
    """restful api for web ui user login/profile page"""
    method_decorators = [authenticate]

    def get(self, cmd):
        """restful api get"""

        if not cmd:
            abort(404, 'does not get command')

        from analysis.ui.database import trigger_user
        if cmd == 'initialPage':
            if not UiConfig.db_enable:
                return json.dumps({'connectDB': False}), 200, CORS

            has_user = True if trigger_user.count_user() > 0 else False
            return json.dumps({'connectDB': True, 'hasUser': has_user}), 200, CORS
        
        args = UI_USER_GET_PARSER.parse_args()
        if cmd == 'userVerify':
            uid = args.get('userId')
            jwt = JwtUtil(UiConfig.jwt_secret)
            token = request.headers.get("Authorization")
            token_vaild, msg = jwt.is_token_vaild(token, uid)
            return json.dumps({'vaild': token_vaild, 'msg': msg}), 200, CORS

        if cmd == 'signOut':
            uid = args.get('userId')
            res = LocalCache.pop(uid)
            return json.dumps({'signOut': res}), 200, CORS

        if cmd == 'ipList':
            uid = args.get('userId')       
            return json.dumps({'ipList': trigger_user.user_ip_list(uid)}), 200, CORS

        if cmd == 'getIpData':
            ip_addrs = args.get('ipAddrs')
            response_obj = trigger_user.ip_info_list(ip_addrs)
            return json.dumps(response_obj), 200, CORS

        if cmd == 'deleteIp':
            uid = args.get('userId')
            ip_addrs = args.get('ipAddrs')
            return json.dumps({'success': trigger_user.delete_ip(uid, ip_addrs)}), 200, CORS


    def post(self, cmd):
        """restful api post"""
        if not cmd:
            abort(404, 'does not post command')
        
        args = UI_USER_POST_PARSER.parse_args()
        jwt = JwtUtil(UiConfig.jwt_secret)
        from analysis.ui.database import trigger_user
        if cmd == 'login':
            email = args.get('email')
            pwd = args.get('password')
            res, name = trigger_user.user_exist(email, pwd)
            if res == -1:
                return json.dumps({'login': False, 'msg': '账号密码不正确'}), 200, CORS
            # check if token is existed and valid
            val = LocalCache.get(key=res)
            if val is not None:
                token_valid, msg = jwt.is_token_vaild(val, res)
                if token_valid:
                    return json.dumps({'login': False, 'msg': '您的账号已于其他平台上登录'}), 200, CORS
            token = jwt.encode({'user_id': res})
            # put token into cache
            LocalCache.put(res, token)
            return json.dumps({'login': True, 'user_id': res, 'user_name': name, 
                                'token': token}), 200, CORS

        if cmd == 'signup':
            email = args.get('email')
            pwd = args.get('password')
            name = args.get('name')
            res, dup = trigger_user.create_user(email, pwd, name)
            if res:
                return json.dumps({'signup': res}), 200, CORS
            return json.dumps({'signup': res, 'duplicate': dup}), 200, CORS
        
        if cmd == 'getBasicInfo':
            uid = args.get('userId')
            name, description = trigger_user.get_user_info(uid)
            return json.dumps({'name': name, 'description': description}), 200, CORS
        
        if cmd == 'changePasswd':
            uid = args.get('userId')
            pwd = args.get('password')
            new_pwd = args.get('newPasswd')
            return json.dumps(trigger_user.change_user_pwd(uid, pwd, new_pwd)), 200, CORS

        if cmd == 'changeBasicInfo':
            uid = args.get('userId')
            name = args.get('name')
            description = args.get('description')
            return json.dumps(trigger_user.change_user_info(uid, name, description)), 200, CORS

        if cmd == 'createAdmin':
            has_user = True if trigger_user.count_user() > 0 else False
            if has_user:
                return json.dumps({'success': False, 'reason': 'duplicate'}), 200, CORS
            pwd = args.get('password')
            return json.dumps(trigger_user.create_admin(pwd)), 200, CORS
        
        if cmd == 'addNewIp':
            uid = args.get('userId')
            ip_addrs = args.get('ipAddrs')
            ip_port = args.get('ipPort')
            server_user = args.get('serverUser')
            server_password = args.get('serverPassword')
            description = args.get("description")
            return json.dumps({'success': trigger_user.add_ip(uid, ip_addrs, ip_port, 
                                server_user, server_password, description)}), 200, CORS

        if cmd == 'updateIp':
            uid = args.get('userId')
            ip_addrs = args.get('ipAddrs')
            ip_port = args.get('ipPort')
            server_user = args.get('serverUser')
            server_password = decode_server_password(args.get('serverPassword'))
            description = args.get("description")
            return json.dumps({'success': trigger_user.update_ip(uid, ip_addrs, ip_port, 
                                server_user, server_password, description)}), 200, CORS

        if cmd == 'testConnect':
            ip_addrs = args.get('ipAddrs')
            ip_port = args.get('ipPort')
            server_user = args.get('serverUser')
            server_password = decode_server_password(args.get('serverPassword'))
            return json.dumps(verify_server_connectivity(ip_addrs, ip_port, server_user, server_password)), 200, CORS
        
        return '', 200, CORS