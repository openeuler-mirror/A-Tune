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
Restful api for configurator, in order to provide the method of put and get.
"""

from flask import abort
from flask import current_app
from flask_restful import Resource
from flask_restful import marshal_with_field
from resources.parser import property_put_parser
from resources.parser import configurator_get_parser
from resources.field import configurator_put_field
from plugin.plugin import CPI


class Configurator(Resource):
    @marshal_with_field(configurator_put_field)
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
        args = property_put_parser.parse_args()
        current_app.logger.info(args)
        section = args.get("section").upper()
        modules = section.split(".")
        submodule = None
        if len(modules) > 1:
            submodule = modules[1]
        configurators = CPI.get_configurators(modules[0], submodule)
        if len(configurators) < 1:
            result["status"] = "module %s is not exist" % (section)
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

    def get(self):
        """
        calling the cpi check method to check the value of the given key
        :param section:  The section of the cpi
        :param key: the key to be get
        :param value: the expect value
        :returns status: the status compare the expect value with the real value
        :returns value: the system real value
        """
        result = {}
        args = configurator_get_parser.parse_args()
        current_app.logger.info(args)
        section = args.get("section").upper()
        key = args.get("key")
        value = args.get("value", "")

        modules = section.split(".")
        submodule = None
        if len(modules) > 1:
            submodule = modules[1]
        configurators = CPI.get_configurators(modules[0], submodule)

        if len(configurators) < 1:
            abort(404)

        configurator = configurators[0]
        realValue = configurator.get(key)
        result["value"] = realValue
        if realValue:
            if configurator._check(value, realValue):
                result["status"] = "OK"
            else:
                result["status"] = realValue
        else:
            result["status"] = "UNKNOWN"

        return result, 200

