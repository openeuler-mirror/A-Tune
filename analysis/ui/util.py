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
import paramiko

from paramiko import ssh_exception
from paramiko.ssh_exception import AuthenticationException


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
