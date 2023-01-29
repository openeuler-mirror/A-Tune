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
# Create: 2023-01-14


"""
Provide utility functions for ui
"""
import socket
import base64
from datetime import datetime, timedelta

import jwt
import paramiko
from paramiko import ssh_exception
from paramiko.ssh_exception import AuthenticationException


class JwtUtil:
    """jwt util class"""


    def __init__(self, secret):
        self.secret = secret

    def encode(self, payload, expires=1):
        """encode payload and set expires time"""
        payload['exp'] = datetime.utcnow().timestamp() + timedelta(days=expires).total_seconds()

        return jwt.encode(payload=payload, key=self.secret, algorithm='HS256')

    def is_token_vaild(self, token, uid):
        """Judge whether the token is valid"""
        try:
            payload = jwt.decode(jwt=token, key=self.secret, algorithms=['HS256'])
            if payload['user_id'] != uid:
                return False, "Invalid user"
            return True, ""
        except jwt.exceptions.InvalidSignatureError:
            return False, "Invalid token"
        except jwt.exceptions.ExpiredSignatureError:
            return False, "Token expired"
        except Exception:
            return False, "Verification failed"
        

def verify_server_connectivity(ip_addrs, ip_port, server_user, server_password):
    """Verify server connectivity"""
    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    res = {}
    try:
        conn.connect(ip_addrs, port=ip_port, username=server_user, password=server_password, timeout=3)
        res = {"success": True, "msg": "服务器连接成功"}
    except AuthenticationException:
        res = {"success": False, "msg": "用户名或密码错误"}
    except socket.timeout:
        res = {"success": False, "msg": "服务器连接超时"}
    except ssh_exception.NoValidConnectionsError:
        res = {"success": False, "msg": "服务器端口错误"}
    return res


def decode_server_password(pwd):
    return base64.b64decode(pwd)