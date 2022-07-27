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
Restful api for monitor, in order to provide the method of post and get.
"""

import getopt
from flask import abort
from flask import current_app
from flask_restful import reqparse, Resource

from analysis.atuned import MPI_INSTANCE
from analysis.atuned.parser import MONITOR_GET_PARSER
from analysis.atuned.parser import MONITOR_POST_PARSER

PARSER = reqparse.RequestParser()


class Monitor(Resource):
    """restful api for monitor, in order to provide the method of post and get"""
    module = "module"
    purpose = "purpose"

    def get(self):
        """provide the method of get"""
        result = {}
        args = MONITOR_GET_PARSER.parse_args()
        current_app.logger.info(args)
        module = args.get(self.module)
        purpose = args.get(self.purpose, None)
        fmt = args.get("fmt")
        path = args.get("path")
        para = args.get("para")

        path = None if path.strip() == "" else path
        para = None if para.strip() == "" else para
        monitors = MPI_INSTANCE.get_monitors(module, purpose)
        if len(monitors) < 1:
            result["status"] = f"module: {module}, purpose:{purpose} is not exist"
            return result, 200

        monitor = monitors[0]
        ret = monitor.report(fmt, path, para)
        if isinstance(ret, Exception):
            result["value"] = str(ret)
            result["status"] = "FAILED"
            return result, 200

        result["status"] = "OK"
        result["value"] = ret
        return result, 200

    def post(self):
        """provide the method of post"""
        result = {}
        args = MONITOR_POST_PARSER.parse_args()
        current_app.logger.info(args)

        monitors = MPI_INSTANCE.get_monitors(args.get(self.module), args.get(self.purpose, None))

        if len(monitors) < 1:
            abort(404)

        monitor = monitors[0]
        ret = monitor.report("data", None, args.get("field"))
        opts, args = getopt.getopt(args.get("field").split(";")[1].split(), None,
                                   ['fields=', 'addr-merge='])
        opt = []
        for option, value in opts:
            if option in "--fields":
                opt.append(value)

        events = []
        for index, _ in enumerate(ret):
            if isinstance(ret[index], list):
                event = {}
                for i in range(len(ret[index])):
                    event[opt[i]] = ret[index][i]
                events.append(event)
            else:
                result[opt[index]] = ret[index]

        if len(events) > 0:
            result["data"] = events
        return result, 200
