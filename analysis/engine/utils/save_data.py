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
# Create: 2023-1-18

"""
Save tuning or analysis data to file and database
"""

import string
from flask import request

from analysis.engine.utils import utils
from analysis.engine.config import EngineConfig


def save_tuning_data(args, out_queue):
    save_tuning_data_file(args, out_queue)
    if EngineConfig.db_enable:
        save_tuning_data_database(args)


def save_tuning_data_file(args, out_queue):
    if args["iterations"] == -1:
        value = args["line"][:-1].split(" ")
        utils.add_data_to_file(value[2] + "," + value[3], "w", args["prj_name"])
        return

    if args["iterations"] == 0:
        total_eval = args["line"].split("|")[3].split("=")[1]
        utils.add_data_to_file(utils.get_opposite_num(total_eval, True), "a", args["prj_name"])
        params = utils.get_string_split(args["line"], 5, 0, "")
        params += utils.get_string_split(args["line"], 4, 0, "evaluation-")
        if len(args["line"].split("|")[4].split(",")) > 1:
            params += "evaluation-TOTAL" + ","
        params = params[:-1]
        utils.add_data_to_file(params, "a", args["prj_name"])

    if args["iterations"] != 0 and len(args["value"]) != 0:
        params = utils.get_time_difference(args["line"].split("|")[2],
                                            args["line"].split("|")[1])
        params += "," + utils.get_string_split(args["line"], 5, 1, "")
        if len(args["line"].split("|")[4].split(",")) > 1:
            for each_eval in args["line"].split("|")[4].split(","):
                params += utils.get_opposite_num(each_eval.split("=")[1], False) + ","
        total_eval = args["line"].split("|")[3].split("=")[1]
        params += utils.get_opposite_num(total_eval, True)
        utils.add_data_to_file(params, "a", args["prj_name"])
        out_queue.send(args.get("value"))

    if args["iterations"] == args["max_iter"]:
        utils.add_data_to_file("END", "a", args["prj_name"])
        utils.change_file_name(args["prj_name"], "finished")


def save_tuning_data_database(args):
    from analysis.ui.database import trigger_tuning
    if args["iterations"] == -1:
        value = args["line"][:-1].split(" ")
        client_ip = request.remote_addr
        trigger_tuning.add_new_tuning(args['prj_name'], value[2], args['max_iter'],
                                            client_ip)
        return

    if args["iterations"] == 0:
        total_eval = args["line"].split("|")[3].split("=")[1]
        trigger_tuning.change_tuning_baseline(args['prj_name'],
                                                    utils.get_opposite_num(total_eval, True))
        trigger_tuning.create_tuning_data_table(args['prj_name'].rstrip(string.digits)[:-1], args['line'])

    if args["iterations"] != 0 and len(args["value"]) != 0:
        table_name = trigger_tuning.add_tuning_data(args['prj_name'], args['iterations'],
                                                        args['line'])
        if table_name is not None:
            trigger_tuning.change_tuning_status(table_name, args['prj_name'])


def save_analysis_or_collection_data(args, client_ip):
    if utils.is_analysis_data(args['collect_data']):
        return save_analysis_data(args, client_ip)
    else:
        return -1


def save_analysis_data(args, client_ip):
    from analysis.ui.database import trigger_analysis
    curr_id = args['collect_id']
    if curr_id == -1:
        curr_id = trigger_analysis.add_new_collection(client_ip)
    if curr_id != -1:
        types = args['type']
        status = args['status']
        workload = args['workload_type']

        if types == 'csv' and status == 'running':
            trigger_analysis.add_collection_data(curr_id, client_ip, args['collect_data'])
        elif types == 'csv' and status == 'finished':
            trigger_analysis.change_collection_status(curr_id, status, types)
            trigger_analysis.change_collection_info(curr_id, workload)
        elif types == 'log' and status == 'running':
            trigger_analysis.add_analysis_log(curr_id, args['collect_data'])
        else:
            trigger_analysis.change_collection_status(curr_id, status, types)
            trigger_analysis.change_collection_info(curr_id, workload)
    return curr_id