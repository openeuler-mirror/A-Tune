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
UI_TUNING_GET_PARSER.add_argument('uid', type=int, help="user id")
UI_TUNING_GET_PARSER.add_argument('status', type=str, help="tuning status")
UI_TUNING_GET_PARSER.add_argument('name', type=str, help="tuning name")
UI_TUNING_GET_PARSER.add_argument('newName', type=str, help="new tuning name")
UI_TUNING_GET_PARSER.add_argument('line', type=str, help="tuning round")

UI_ANALYSIS_GET_PARSER = reqparse.RequestParser()
UI_ANALYSIS_GET_PARSER.add_argument('uid', type=int, help="user id")
UI_ANALYSIS_GET_PARSER.add_argument('name', type=str, help="analysis name")
UI_ANALYSIS_GET_PARSER.add_argument('newName', type=str, help="new analysis name")
UI_ANALYSIS_GET_PARSER.add_argument('csvLine', type=str, help="analysis round")
UI_ANALYSIS_GET_PARSER.add_argument('logLine', type=str, help="analysis round")

UI_USER_GET_PARSER = reqparse.RequestParser()
UI_USER_GET_PARSER.add_argument('email', type=str, help="user email")
UI_USER_GET_PARSER.add_argument('name', type=str, help="user name")
UI_USER_GET_PARSER.add_argument('password', type=str, help="user password")
UI_USER_GET_PARSER.add_argument('userId', type=int, help="user id")
UI_USER_GET_PARSER.add_argument('ipAddrs', type=str, help="ip address")
UI_USER_GET_PARSER.add_argument('newPasswd', type=str, help="new password for changing")
