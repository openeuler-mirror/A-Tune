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
# Create: 2020-07-17

"""
Parameters used for restful api.
"""

from flask_restful import reqparse

OPTIMIZER_POST_PARSER = reqparse.RequestParser()
OPTIMIZER_POST_PARSER.add_argument('max_eval', type=int, required=True,
                                   help="max_eval cannot be null")
OPTIMIZER_POST_PARSER.add_argument('knobs', type=list, location='json',
                                   help="knobs list cannot be null")
OPTIMIZER_POST_PARSER.add_argument('engine',
                                   choices=('random', 'forest', 'gbrt', 'extraTrees',
                                            'bayes', 'abtest', 'lhs', 'tpe', 'gridsearch',
                                            'traverse'),
                                   help='engine choice: {error_msg}')
OPTIMIZER_POST_PARSER.add_argument('random_starts', type=int, location='json',
                                   help="random_starts cannot be null")
OPTIMIZER_POST_PARSER.add_argument('x_ref', type=list, location='json',
                                   help="the reference of x0 list")
OPTIMIZER_POST_PARSER.add_argument('y_ref', type=list, location='json',
                                   help="the reference of y0 list")
OPTIMIZER_POST_PARSER.add_argument('feature_filter', type=bool, location='json',
                                   help="the feature_filter enabled")
OPTIMIZER_POST_PARSER.add_argument('split_count', type=int, location='json',
                                   help="split_count cannot be null")
OPTIMIZER_POST_PARSER.add_argument('sel_feature', type=bool, location='json',
                                   help="enable the feature selection or not")
OPTIMIZER_POST_PARSER.add_argument('noise', type=float, location='json',
                                   help="the noise can not be null")
OPTIMIZER_POST_PARSER.add_argument('prj_name', type=str, location='json',
                                   help="prj_name cannot be null")
OPTIMIZER_POST_PARSER.add_argument('feature_selector', choices=('wefs', 'vrfs'),
                                   help="importance feature selector: {error_msg}")

OPTIMIZER_PUT_PARSER = reqparse.RequestParser()
OPTIMIZER_PUT_PARSER.add_argument('iterations', type=int, required=True,
                                  help="iterations cannot be null")
OPTIMIZER_PUT_PARSER.add_argument('value', type=str, required=True,
                                  help="value cannot be null")
OPTIMIZER_PUT_PARSER.add_argument('line', type=str, required=True,
                                  help="line cannot be null")
OPTIMIZER_PUT_PARSER.add_argument('prj_name', type=str, required=True,
                                  help="project name cannot be null")
OPTIMIZER_PUT_PARSER.add_argument('max_iter', type=int, required=True,
                                  help="max iterations cannot be null")

CLASSIFICATION_POST_PARSER = reqparse.RequestParser()
CLASSIFICATION_POST_PARSER.add_argument('modelpath', required=True,
                                        help="The modelfile to be used")
CLASSIFICATION_POST_PARSER.add_argument('data',
                                        help="The data path to be used")
CLASSIFICATION_POST_PARSER.add_argument('model',
                                        help="The model self trained to be used")

TRAIN_POST_PARSER = reqparse.RequestParser()
TRAIN_POST_PARSER.add_argument('datapath', required=True,
                               help="The datapath can not be null")
TRAIN_POST_PARSER.add_argument('outputpath', required=True,
                               help="The output path can not be null")
TRAIN_POST_PARSER.add_argument('modelpath', required=True,
                               help="The model path can not be null")

DETECT_POST_PARSER = reqparse.RequestParser()
DETECT_POST_PARSER.add_argument('appname', required=True, help="The appname path can not be null")
DETECT_POST_PARSER.add_argument('detectpath', type=str, help="The path of file to be detect")

TRANSFER_PUT_PARSER = reqparse.RequestParser()
TRANSFER_PUT_PARSER.add_argument('type', type=str, required=True,
                                 help="type of data can not be null")
TRANSFER_PUT_PARSER.add_argument('collect_id', type=int, required=True,
                                 help="Collection id can not be null")
TRANSFER_PUT_PARSER.add_argument('status', type=str, required=True, help="Status can not be null")
TRANSFER_PUT_PARSER.add_argument('collect_data', type=str, required=False, help="Collection data")
TRANSFER_PUT_PARSER.add_argument('workload_type', type=str, required=False, help="Workload type")

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
