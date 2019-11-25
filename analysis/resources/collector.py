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
Restful api with collector, in order to provide the method of post.
"""

from flask import current_app
from flask_restful import reqparse, Resource
from flask_restful import request, marshal_with, marshal_with_field
import os
import pandas as pd
from resources.field import profile_get_field
from resources.parser import collector_post_parser
from plugin.plugin import CPI
from plugin.plugin import MPI
from utils.npipe import getNpipe

parser = reqparse.RequestParser()


class Collector(Resource):
    @marshal_with_field(profile_get_field)
    def post(self):
        args = collector_post_parser.parse_args()
        current_app.logger.info(args)
        monitors = []
        mpis = []
        for monitor in args.get("monitors"):
            monitors.append([monitor["module"], monitor["purpose"], monitor["field"]])
            mpis.append(MPI.get_monitor(monitor["module"], monitor["purpose"]))
        collect_num = args.get("sample_num")

        nPipe = getNpipe(args.get("pipe"))
        current_app.logger.info(monitors)

        data = []

        for i in range(collect_num):
            raw_data = MPI.get_monitors_data(monitors, mpis)
            current_app.logger.info(raw_data)
            
            float_data = list()
            for x in raw_data:
                float_data.append(float(x))

            data.append(float_data)

            str_data = [str(round(data, 3)) for data in float_data]
            nPipe.write(" ".join(str_data) + "\n")

        path = "/tmp/test.csv"
        save_file(path, data)
        result = {}
        result["path"] = path
        return result, 200


def save_file(file_name, datas):
    print(datas)
    writer = pd.DataFrame(columns=None, data=datas)
    writer.to_csv(file_name, encoding='utf-8', header=0, index=False)
