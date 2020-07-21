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
Restful api with collector, in order to provide the method of post.
"""
import os

from flask import current_app, abort
from flask_restful import reqparse, Resource
from flask_restful import marshal_with_field
import pandas as pd
from analysis.atuned.field import PROFILE_GET_FIELD
from analysis.atuned.parser import COLLECTOR_POST_PARSER
from analysis.plugin.plugin import MPI
from analysis.atuned.utils.npipe import get_npipe

PARSER = reqparse.RequestParser()


class Collector(Resource):
    """restful api with collector, in order to provide the method of post"""
    monitors = "monitors"

    @marshal_with_field(PROFILE_GET_FIELD)
    def post(self):
        """provide the method of post"""
        args = COLLECTOR_POST_PARSER.parse_args()
        current_app.logger.info(args)
        n_pipe = get_npipe(args.get("pipe"))
        if n_pipe is None:
            abort(404)

        monitors = []
        mpis = []
        for monitor in args.get(self.monitors):
            monitors.append([monitor["module"], monitor["purpose"], monitor["field"]])
            mpis.append(MPI.get_monitor(monitor["module"], monitor["purpose"]))
        collect_num = args.get("sample_num")
        if int(collect_num) < 1:
            abort("sample_num must be greater than 0")

        current_app.logger.info(monitors)

        data = []

        for _ in range(collect_num):
            raw_data = MPI.get_monitors_data(monitors, mpis)
            current_app.logger.info(raw_data)

            float_data = list()
            for num in raw_data:
                float_data.append(float(num))

            data.append(float_data)

            str_data = [str(round(data, 3)) for data in float_data]
            n_pipe.write(" ".join(str_data) + "\n")

        n_pipe.close()

        path = "/run/atuned/test.csv"
        save_file(path, data)
        result = {}
        result["path"] = path
        return result, 200


def save_file(file_name, datas):
    """save file"""
    path = os.path.dirname(file_name.strip())
    if not os.path.exists(path):
        os.makedirs(path, 0o750)
    writer = pd.DataFrame(columns=None, data=datas)
    writer.to_csv(file_name, encoding='utf-8', header=0, index=False)
