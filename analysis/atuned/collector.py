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

from analysis.atuned import MPI_INSTANCE
from analysis.atuned.field import PROFILE_GET_FIELD
from analysis.atuned.parser import COLLECTOR_POST_PARSER
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
        monitors = []
        mpis = []
        field_name = []
        for monitor in args.get(self.monitors):
            monitors.append([monitor["module"], monitor["purpose"], monitor["field"]])
            mpis.append(MPI_INSTANCE.get_monitor(monitor["module"], monitor["purpose"]))
            opts = monitor["field"].split(";")[1].split()
            for opt in opts:
                if opt.split("=")[0] in "--fields":
                    field_name.append(f"{monitor['module']}.{monitor['purpose']}.{opt.split('=')[1]}")
        field_key = field_name[:]
        data_type = args.get("data_type")
        if data_type != "":
            field_name.append("workload.type")
            field_name.append("workload.appname")

        collect_num = args.get("sample_num")
        if int(collect_num) < 1:
            abort("sample_num must be greater than 0")

        current_app.logger.info(monitors)

        data = []
        data_field = []
        for _ in range(collect_num):
            raw_data = MPI_INSTANCE.get_monitors_data(monitors, mpis)
            current_app.logger.info(raw_data)

            float_data = list()
            for num in raw_data:
                float_data.append(float(num))

            str_data = [str(round(data, 3)) for data in float_data]
            if n_pipe is not None:
                ret = []
                for key, val in zip(field_key, str_data):
                    ret.append(key + ":" + val)
                n_pipe.write(" ".join(ret) + "\n")

            data_field.append(float_data.copy())
            if data_type != "":
                for type_name in data_type.split(":"):
                    float_data.append(type_name)
            data.append(float_data)

        data_average = [sum(elem) / len(elem) for elem in zip(*data_field)]
        data_result = {}
        for index, _ in enumerate(data_average):
            data_result[field_name[index]] = data_average[index]
        if n_pipe is not None:
            n_pipe.close()

        path = args.get("file")
        save_file(path, data, field_name)
        result = {}
        result["path"] = path
        result["data"] = data_result
        return result, 200


def save_file(file_name, datas, field):
    """save file"""
    path = os.path.dirname(file_name.strip())
    os.makedirs(path, 0o750, exist_ok=True)
    writer = pd.DataFrame(columns=field, data=datas)
    writer.to_csv(file_name, encoding='utf-8', index=False)
