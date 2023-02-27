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
# Create: 2022-6-25

"""
Parameters used for restful api.
"""

from flask_restful import reqparse


UI_TUNING_GET_PARSER = reqparse.RequestParser()
UI_TUNING_GET_PARSER.add_argument('uid', type=int, help="user id", location='args')
UI_TUNING_GET_PARSER.add_argument('tid', type=int, help="tuning id", location='args')
UI_TUNING_GET_PARSER.add_argument('status', type=str, help="tuning status", location='args')
UI_TUNING_GET_PARSER.add_argument('name', type=str, help="tuning name", location='args')
UI_TUNING_GET_PARSER.add_argument('newName', type=str, help="new tuning name", location='args')
UI_TUNING_GET_PARSER.add_argument('line', type=str, help="tuning round", location='args')
UI_TUNING_GET_PARSER.add_argument('pageNum', type=int, help="page number", location='args')
UI_TUNING_GET_PARSER.add_argument('pageSize', type=int, help="page size", location='args')
UI_TUNING_GET_PARSER.add_argument('description', type=str, help="tuning description", location='args')

UI_ANALYSIS_GET_PARSER = reqparse.RequestParser()
UI_ANALYSIS_GET_PARSER.add_argument('uid', type=int, help="user id", location='args')
UI_ANALYSIS_GET_PARSER.add_argument('cid', type=int, help="analysis id", location='args')
UI_ANALYSIS_GET_PARSER.add_argument('pageNum', type=int, help="page number", location='args')
UI_ANALYSIS_GET_PARSER.add_argument('pageSize', type=int, help="page size", location='args')
UI_ANALYSIS_GET_PARSER.add_argument('name', type=str, help="analysis name", location='args')
UI_ANALYSIS_GET_PARSER.add_argument('newName', type=str, help="new analysis name", location='args')
UI_ANALYSIS_GET_PARSER.add_argument('csvLine', type=str, help="analysis round", location='args')
UI_ANALYSIS_GET_PARSER.add_argument('logLine', type=str, help="analysis round", location='args')
UI_ANALYSIS_GET_PARSER.add_argument('description', type=str, help="analysis description", location='args')

UI_COMMAND_GET_PARSER = reqparse.RequestParser()
UI_COMMAND_GET_PARSER.add_argument('uid', type=int, help="user id", location='args')
UI_COMMAND_GET_PARSER.add_argument('cid', type=int, help="command id", location='args')
UI_COMMAND_GET_PARSER.add_argument('pageNum', type=int, help="page number", location='args')
UI_COMMAND_GET_PARSER.add_argument('pageSize', type=int, help="page size", location='args')
UI_COMMAND_GET_PARSER.add_argument('description', type=str, help="command description", location='args')

UI_USER_GET_PARSER = reqparse.RequestParser()
UI_USER_GET_PARSER.add_argument('userId', type=int, help="user id", location='args')
UI_USER_GET_PARSER.add_argument('ipAddrs', type=str, help="ip address", location='args')

UI_USER_POST_PARSER = reqparse.RequestParser()
UI_USER_POST_PARSER.add_argument('email', type=str, help="user email", location='json')
UI_USER_POST_PARSER.add_argument('name', type=str, help="user name", location='json')
UI_USER_POST_PARSER.add_argument('password', type=str, help="user password", location='json')
UI_USER_POST_PARSER.add_argument('userId', type=int, help="user id", location='json')
UI_USER_POST_PARSER.add_argument('description', type=str, help="user description", location='json')
UI_USER_POST_PARSER.add_argument('newPasswd', type=str, help="new password for changing", location='json')
UI_USER_POST_PARSER.add_argument('ipAddrs', type=str, help="ip address", location='json')
UI_USER_POST_PARSER.add_argument('ipPort', type=str, help="ip port", location='json')
UI_USER_POST_PARSER.add_argument('serverUser', type=str, help="server user", location='json')
UI_USER_POST_PARSER.add_argument('serverPassword', type=str, help="server password", location='json')