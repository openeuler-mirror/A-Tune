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
Restful api for monitor, in order to provide the method of post and get.
"""

from flask import abort
from flask import current_app
from flask_restful import reqparse, Resource
from resources.parser import monitor_get_parser
from resources.parser import monitor_post_parser
from plugin.plugin import MPI
import getopt

parser = reqparse.RequestParser()


class Monitor(Resource):
    def get(self):
        result = {}
        args = monitor_get_parser.parse_args()
        current_app.logger.info(args)
        module = args.get("module")
        purpose = args.get("purpose", None)
        fmt = args.get("fmt")
        path = args.get("path")
        para = args.get("para")

        monitors = MPI.get_monitors(module, purpose)
        if len(monitors) < 1:
            return result, 200

        monitor = monitors[0]

        ret = monitor.report(fmt, path, para)
        if ret is not None:
            result["status"] = str(ret)
        else:
            result["status"] = "OK"

        return result, 200

    def post(self):
        result = {}
        args = monitor_post_parser.parse_args()
        current_app.logger.info(args)

        monitors = []
        module = args.get("module")
        purpose = args.get("purpose", None)
        field = args.get("field")

        monitors = MPI.get_monitors(module, purpose)

        if len(monitors) < 1:
            abort(404)

        monitor = monitors[0]
        ret = monitor.report("data", None, field)
        opts, args = getopt.getopt(field.split(";")[1].split(), None, ['fields=', 'addr-merge='])
        opt = []
        for o, v in opts:
            if o in ("--fields"):
                opt.append(v)

        events = []
        for index in range(len(ret)):
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
    
