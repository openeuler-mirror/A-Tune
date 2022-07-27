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
Restful api for profile, in order to provide the method of get and put.
"""
from flask import abort
from flask import current_app
from flask_restful import Resource

from analysis.atuned import CPI_INSTANCE
from analysis.atuned.parser import PROFILE_GET_PARSER, PROFILE_PUT_PARSER


class Profile(Resource):
    """provide the method of get and put for profile"""
    section = "section"

    def put(self):
        """
        resume the profile
        """
        result = {}
        args = PROFILE_PUT_PARSER.parse_args()
        current_app.logger.info(args)
        section = args.get(self.section).upper()
        modules = section.split(".")
        submodule = None
        if len(modules) > 1:
            submodule = modules[1]
        configurators = CPI_INSTANCE.get_configurators(modules[0], submodule)
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

    def get(self):
        """
        backup the profile
        """
        result = {}
        args = PROFILE_GET_PARSER.parse_args()
        current_app.logger.info(args)
        section = args.get(self.section).upper()
        config = args.get("config")
        backup_dir = args.get("path")

        modules = section.split(".")
        submodule = modules[1] if len(modules) > 1 else None
        configurators = CPI_INSTANCE.get_configurators(modules[0], submodule)

        if len(configurators) < 1:
            result["status"] = "FAILED"
            result["value"] = f"module: {modules[0]}, submodule: {submodule} is not exist"
            return result, 200

        configurator = configurators[0]
        real_value = configurator.backup(config, backup_dir)
        if isinstance(real_value, Exception):
            result["status"] = "FAILED"
            result["value"] = str(real_value)
        else:
            if real_value is None:
                result["status"] = "FAILED"
                result["value"] = "UNKNOWN"
            else:
                result["status"] = "SUCCESS"
                result["value"] = real_value

        return result, 200
