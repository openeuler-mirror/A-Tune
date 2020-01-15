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
Restful api for optimizer, in order to provide the method of post, get, put and delete.
"""
import uuid
import logging
from multiprocessing import Pipe
from flask import abort
from flask_restful import reqparse, Resource

from analysis.resources.parser import OPTIMIZER_POST_PARSER, OPTIMIZER_PUT_PARSER
from analysis.utils import task_cache
from optimizer import optimizer

LOGGER = logging.getLogger(__name__)

PARSER = reqparse.RequestParser()


class Optimizer(Resource):
    """restful api for optimizer, in order to provide the method of post, get, put and delete"""
    task_id_info = "taskid"
    pipe = "pipe"

    def get(self, task_id=None):
        """provide the method of get"""
        result = []
        if not task_id:
            tasks_all = task_cache.TasksCache.get_instance().get_all()
            for task in tasks_all:
                result.append(task)
        else:
            task = task_cache.TasksCache.get_instance().get(task_id)
            if not task:
                abort(404, "{0} {1} not found".format(self.task_id_info, task_id))
            result.append(task_id)
        return result, 200

    def post(self):
        """provide the method of post"""
        args = OPTIMIZER_POST_PARSER.parse_args()
        LOGGER.info(args)
        if args["max_eval"] < 11:
            LOGGER.error("the max iterations %s must be greater than 10", args["max_eval"])
            abort(400, "the max iterations {} must be greater than 10".format(args["max_eval"]))
        task_id = str(uuid.uuid1())

        parent_conn, child_conn = Pipe()
        result = {}
        engine = optimizer.Optimizer(task_id, args["knobs"], child_conn,
                                     max_eval=args.get("max_eval"))
        engine.start()

        value = {}
        value["process"] = engine
        value[self.pipe] = parent_conn
        task_cache.TasksCache.get_instance().set(task_id, value)

        result["task_id"] = task_id
        result["status"] = "OK"
        return result, 200

    def put(self, task_id):
        """provide the method of put"""
        if not task_id:
            abort(404, "task id does not exist")
        task = task_cache.TasksCache.get_instance().get(task_id)
        if not task:
            abort(404, "taskid {0} not found".format(task_id))

        args = OPTIMIZER_PUT_PARSER.parse_args()
        LOGGER.info(args)
        out_queue = task[self.pipe]
        if args["iterations"] != 0:
            out_queue.send(args.get("value"))

        result = {}
        values = out_queue.recv()
        if isinstance(values, Exception):
            abort(404, "failed to get optimization results, err: {}".format(values))
        params = ["%s=%s" % (k, v) for k, v in values.items()]
        result["param"] = ",".join(params)

        return result, 200

    def delete(self, task_id):
        """provide the method of delete"""
        if not task_id:
            abort(404, "task id does not exist")
        process = task_cache.TasksCache.get_instance().get(task_id)
        if not process:
            abort(404, "{0} {1} not found".format(self.task_id_info, task_id))
        process["process"].stop_process()
        task_cache.TasksCache.get_instance().get(task_id)[self.pipe].close()

        task_cache.TasksCache.get_instance().delete(task_id)
        return {}, 200
