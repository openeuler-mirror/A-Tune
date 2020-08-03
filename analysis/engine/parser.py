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
OPTIMIZER_POST_PARSER.add_argument('engine', \
        choices=('random', 'forest', 'gbrt', 'bayes', 'abtest', 'lhs', 'tpe'),\
        help='engine choice: {error_msg}')
OPTIMIZER_POST_PARSER.add_argument('random_starts', type=int, location='json', help="random_starts cannot be null")
OPTIMIZER_POST_PARSER.add_argument('x_ref', type=list, location='json', help="the reference of x0 list")
OPTIMIZER_POST_PARSER.add_argument('y_ref', type=list, location='json', help="the reference of y0 list")
OPTIMIZER_POST_PARSER.add_argument('feature_filter', type=bool, location='json', help="the feature_filter enabled")
OPTIMIZER_POST_PARSER.add_argument('split_count', type=int, location='json', help="split_count cannot be null")

OPTIMIZER_PUT_PARSER = reqparse.RequestParser()
OPTIMIZER_PUT_PARSER.add_argument('iterations', type=int, required=True,
                                  help="iterations cannot be null")
OPTIMIZER_PUT_PARSER.add_argument('value', type=str, required=True, help="value cannot be null")

CLASSIFICATION_POST_PARSER = reqparse.RequestParser()
CLASSIFICATION_POST_PARSER.add_argument('modelpath', required=True, help="The modelfile to be used")
CLASSIFICATION_POST_PARSER.add_argument('data', help="The data path to be used")
CLASSIFICATION_POST_PARSER.add_argument('model', help="The model self trained to be used")

TRAIN_POST_PARSER = reqparse.RequestParser()
TRAIN_POST_PARSER.add_argument('datapath', required=True, help="The datapath can not be null")
TRAIN_POST_PARSER.add_argument('outputpath', required=True, help="The output path can not be null")
TRAIN_POST_PARSER.add_argument('modelpath', required=True, help="The model path can not be null")
