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
Restful api for configurator, in order to provide the method of put and get.
"""
from flask import abort
from flask import current_app
from flask_restful import Resource
from flask_restful import marshal_with_field

from analysis.atuned import CPI_INSTANCE
from analysis.atuned.parser import PROPERTY_PUT_PARSER
from analysis.atuned.parser import CONFIGURATOR_GET_PARSER
from analysis.atuned.parser import CONFIGURATOR_POST_PARSER
from analysis.atuned.field import CONFIGURATOR_PUT_FIELD


class Configurator(Resource):
    """restful api for configurator, in order to provide the method of put and get"""
    section = "section"

    @marshal_with_field(CONFIGURATOR_PUT_FIELD)
    def put(self):
        """
        calling cpi set method to set the value of the given key
        :param section:  The section of the cpi
        :param key: the key to be set
        :param value: the value of the given key
        :returns status: the status return by the cpi set method
        :returns value: the message return by the cpi set method
        """
        result = {}
        args = PROPERTY_PUT_PARSER.parse_args()
        current_app.logger.info(args)
        section = args.get(self.section).upper()
        modules = section.split(".")
        submodule = None
        if len(modules) > 1:
            submodule = modules[1]
        configurators = CPI_INSTANCE.get_configurators(modules[0], submodule)
        if len(configurators) < 1:
            result["status"] = f"module {section} is not exist"
            return result, 200
        configurator = configurators[0]

        key = args.get("key")
        value = args.get("value")
        params = key + "=" + value
        ret = configurator.set(params)
        if not ret:
            result["status"] = "OK"
        elif isinstance(ret, Warning):
            result["status"] = "WARNING"
            result["value"] = str(ret)
        elif isinstance(ret, Exception):
            result["status"] = "ERROR"
            result["value"] = str(ret)

        return result, 200

    def post(self):
        """
        calling the cpi check method to check the value of the given key
        :param section:  The section of the cpi
        :param key: the key to be get
        :param value: the expect value
        :returns status: the status compare the expect value with the real value
        :returns value: the system real value
        """
        result = {}
        args = CONFIGURATOR_POST_PARSER.parse_args()
        current_app.logger.info(args)
        section = args.get(self.section).upper()
        key = args.get("key")
        value = args.get("value", "")

        modules = section.split(".")
        submodule = None
        if len(modules) > 1:
            submodule = modules[1]
        configurators = CPI_INSTANCE.get_configurators(modules[0], submodule)

        if len(configurators) < 1:
            abort(404)

        configurator = configurators[0]
        real_value = configurator.get(key)
        if isinstance(real_value, Exception):
            result["status"] = str(real_value)
            return result, 200

        result["value"] = real_value
        if real_value:
            if configurator.check(value, real_value):
                result["status"] = "OK"
            else:
                result["status"] = real_value
        else:
            result["status"] = "UNKNOWN"

        return result, 200

    def get(self):
        """
        calling the cpi check method to check the value of the given key
        :param section:  The section of the cpi
        :param key: the key to be get
        :returns status: the status compare the expect value with the real value
        :returns value: the system real value
        """
        result = {}
        args = CONFIGURATOR_GET_PARSER.parse_args()
        current_app.logger.info(args)
        section = args.get(self.section).upper()
        key = args.get("key")

        modules = section.split(".")
        submodule = modules[1] if len(modules) > 1 else modules[0]

        configurators = CPI_INSTANCE.get_configurators(modules[0], submodule)
        if len(configurators) < 1:
            abort(404)

        configurator = configurators[0]
        real_value = configurator.get(key)
        if isinstance(real_value, Exception):
            result["value"] = str(real_value)
            result["status"] = "FAILED"
            return result, 200

        result["value"] = real_value
        result["status"] = "OK"

        return result, 200
