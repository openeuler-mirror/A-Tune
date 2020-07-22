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
# Create: 2019-10-29

"""
Parameters used for restful api.
"""

from flask_restful import reqparse

ANALYSIS_POST_PARSER = reqparse.RequestParser()
ANALYSIS_POST_PARSER.add_argument('appname', required=True, help="The appname to be analysed")
ANALYSIS_POST_PARSER.add_argument('pipe', required=True,
                                  help="The pipe name to send process status")
ANALYSIS_POST_PARSER.add_argument('workload', required=True, help="The workload dict info")
ANALYSIS_POST_PARSER.add_argument('algorithm', required=True, help="The algorithm to be selected")
ANALYSIS_POST_PARSER.add_argument('modelpath', required=True, help="The modelfile to be used")
ANALYSIS_POST_PARSER.add_argument('scaler', required=True, help="The scalerfile to be used")
ANALYSIS_POST_PARSER.add_argument('encoder', required=True, help="The encoderfile to be used")

PROPERTY_PUT_PARSER = reqparse.RequestParser()
PROPERTY_PUT_PARSER.add_argument('section', required=True, help="The section to be configured")
PROPERTY_PUT_PARSER.add_argument('key', required=True, help="The property to be configured")
PROPERTY_PUT_PARSER.add_argument('value', required=True, help="The value to be configured")

CONFIGURATOR_POST_PARSER = reqparse.RequestParser()
CONFIGURATOR_POST_PARSER.add_argument('section', required=True, help="The section to be configured")
CONFIGURATOR_POST_PARSER.add_argument('key', required=True, help="The property to be configured")
CONFIGURATOR_POST_PARSER.add_argument('value', required=False, help="The value to be configured")

CONFIGURATOR_GET_PARSER = reqparse.RequestParser()
CONFIGURATOR_GET_PARSER.add_argument('section', required=True, help="The section to be configured")
CONFIGURATOR_GET_PARSER.add_argument('key', required=True, help="The key to be to be get")

MONITOR_GET_PARSER = reqparse.RequestParser()
MONITOR_GET_PARSER.add_argument('module', required=True, help="The module to be monitor")
MONITOR_GET_PARSER.add_argument('purpose', required=True, help="The purpose of the module")
MONITOR_GET_PARSER.add_argument('fmt', required=True, help="The format of the result")
MONITOR_GET_PARSER.add_argument('path', required=True, help="The path to be generated")
MONITOR_GET_PARSER.add_argument('para', required=True, help="The parameter of get method")

MONITOR_POST_PARSER = reqparse.RequestParser()
MONITOR_POST_PARSER.add_argument('module', required=True, help="The module to be monitor")
MONITOR_POST_PARSER.add_argument('purpose', required=True, help="The purpose of the module")
MONITOR_POST_PARSER.add_argument('field', required=True, help="The field of the monitor")

COLLECTOR_POST_PARSER = reqparse.RequestParser()
COLLECTOR_POST_PARSER.add_argument('sample_num', type=int, required=True,
                                   help="the numbers to be collections")
COLLECTOR_POST_PARSER.add_argument('monitors', type=list, location='json',
                                   help="knobs list cannot be null")
COLLECTOR_POST_PARSER.add_argument('pipe', required=True,
                                   help="The pipe name to send process status")
COLLECTOR_POST_PARSER.add_argument('file', required=True,
                                   help="The file for storing collected data")
COLLECTOR_POST_PARSER.add_argument('data_type', help="The type of collected data")

PROFILE_GET_PARSER = reqparse.RequestParser()
PROFILE_GET_PARSER.add_argument('section', required=True, help="The section to be configured")
PROFILE_GET_PARSER.add_argument('config', required=True, help="The config to be get")
PROFILE_GET_PARSER.add_argument('path', required=True, help="The path to backup to")

PROFILE_PUT_PARSER = reqparse.RequestParser()
PROFILE_PUT_PARSER.add_argument('section', required=True, help="The section to be configured")
PROFILE_PUT_PARSER.add_argument('config', required=True, help="The config to be get")
