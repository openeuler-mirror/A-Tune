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
Restful api for profile, in order to provide the method of get and put.
"""

from flask import abort
from flask import current_app
from flask_restful import Resource
from resources.parser import profile_get_parser, profile_put_parser
from plugin.plugin import CPI


class Profile(Resource):
    '''
    resume the profile
    '''

    def put(self):
        result = {}
        args = profile_put_parser.parse_args()
        current_app.logger.info(args)
        section = args.get("section").upper()
        modules = section.split(".")
        submodule = None
        if len(modules) > 1:
            submodule = modules[1]
        configurators = CPI.get_configurators(modules[0], submodule)
        if len(configurators) < 1:
            abort(404)

        configurator = configurators[0]

        config = args.get("config")
        ret = configurator.resume(config)
        if ret is not None:
            result["status"] = str(ret)
        else:
            result["status"] = "OK"

        return result, 200

    '''
    backup the profile
    '''

    def get(self):
        result = {}
        args = profile_get_parser.parse_args()
        current_app.logger.info(args)
        section = args.get("section").upper()
        config = args.get("config")
        backupDir = args.get("path")

        modules = section.split(".")
        submodule = None
        if len(modules) > 1:
            submodule = modules[1]
        configurators = CPI.get_configurators(modules[0], submodule)

        if len(configurators) < 1:
            abort(404)

        configurator = configurators[0]
        realValue = configurator.backup(config, backupDir)
        if isinstance(realValue, Exception):
            result["status"] = "FAILED"
            result["value"] = "exception"
        else:
            if not realValue:
                result["status"] = "FAILED"
                result["value"] = "UNKNOWN"
            else:
                result["status"] = "SUCCESS"
                result["value"] = realValue

        return result, 200

