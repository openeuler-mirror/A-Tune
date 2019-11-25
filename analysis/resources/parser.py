#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v1.
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
# Create: 2019-10-29

"""
Parameters used for restful api.
"""

from flask_restful import reqparse


analysis_post_parser = reqparse.RequestParser()
analysis_post_parser.add_argument('appname', required=True, help="The appname to be analysed")
analysis_post_parser.add_argument('pipe', required=True,
                                  help="The pipe name to send process status")
analysis_post_parser.add_argument('workload', required=True, help="The workload dict info")
analysis_post_parser.add_argument('algorithm', required=True, help="The algorithm to be selected")
analysis_post_parser.add_argument('modelpath', required=True, help="The modelfile to be used")
analysis_post_parser.add_argument('scaler', required=True, help="The scalerfile to be used")
analysis_post_parser.add_argument('encoder', required=True, help="The encoderfile to be used")

property_put_parser = reqparse.RequestParser()
property_put_parser.add_argument('section', required=True, help="The section to be configured")
property_put_parser.add_argument('key', required=True, help="The property to be configured")
property_put_parser.add_argument('value', required=True, help="The value to be configured")

configurator_get_parser = reqparse.RequestParser()
configurator_get_parser.add_argument('section', required=True, help="The section to be configured")
configurator_get_parser.add_argument('key', required=True, help="The property to be configured")
configurator_get_parser.add_argument('value', required=False, help="The value to be configured")

monitor_get_parser = reqparse.RequestParser()
monitor_get_parser.add_argument('module', required=True, help="The module to be monitor")
monitor_get_parser.add_argument('purpose', required=True, help="The purpose of the module")
monitor_get_parser.add_argument('fmt', required=True, help="The format of the result")
monitor_get_parser.add_argument('path', required=True, help="The path to be generated")
monitor_get_parser.add_argument('para', required=True, help="The parameter of get method")

monitor_post_parser = reqparse.RequestParser()
monitor_post_parser.add_argument('module', required=True, help="The module to be monitor")
monitor_post_parser.add_argument('purpose', required=True, help="The purpose of the module")
monitor_post_parser.add_argument('field', required=True, help="The field of the monitor")

optimizer_post_parser = reqparse.RequestParser()
optimizer_post_parser.add_argument('max_eval', type=int, required=True,
                                   help="max_eval cannot be null")
optimizer_post_parser.add_argument('knobs', type=list, location='json',
                                   help="knobs list cannot be null")

optimizer_put_parser = reqparse.RequestParser()
optimizer_put_parser.add_argument('iterations', type=int, required=True,
                                  help="iterations cannot be null")
optimizer_put_parser.add_argument('value', type=str, required=True, help="value cannot be null")

collector_post_parser = reqparse.RequestParser()
collector_post_parser.add_argument('sample_num', type=int, required=True,
                                   help="the numbers to be collections")
collector_post_parser.add_argument('monitors', type=list, location='json',
                                   help="knobs list cannot be null")
collector_post_parser.add_argument('pipe', required=True,
                                   help="The pipe name to send process status")

classification_post_parser = reqparse.RequestParser()
classification_post_parser.add_argument('modelpath', required=True, help="The modelfile to be used")
classification_post_parser.add_argument('data', help="The data path to be used")
classification_post_parser.add_argument('model', help="The model self trained to be used")


profile_get_parser = reqparse.RequestParser()
profile_get_parser.add_argument('section', required=True, help="The section to be configured")
profile_get_parser.add_argument('config', required=True, help="The config to be get")
profile_get_parser.add_argument('path', required=True, help="The path to backup to")

profile_put_parser = reqparse.RequestParser()
profile_put_parser.add_argument('section', required=True, help="The section to be configured")
profile_put_parser.add_argument('config', required=True, help="The config to be get")

train_post_parser = reqparse.RequestParser()
train_post_parser.add_argument('datapath', required=True, help="The datapath can not be null")
train_post_parser.add_argument('outputpath', required=True, help="The output path can not be null")
train_post_parser.add_argument('modelpath', required=True, help="The model path can not be null")
