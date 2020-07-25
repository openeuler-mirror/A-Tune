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
Restful api for optimizer, in order to provide the method of post, get, put and delete.
"""
import uuid
import logging
from multiprocessing import Pipe
from flask import abort
from flask_restful import reqparse, Resource

from analysis.engine.parser import OPTIMIZER_POST_PARSER, OPTIMIZER_PUT_PARSER
from analysis.engine.utils import task_cache
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
        task_id = str(uuid.uuid1())

        parent_conn, child_conn = Pipe()
        result = {}
        engine = optimizer.Optimizer(task_id, args["knobs"], child_conn, engine=args.get("engine"),
                                     max_eval=args.get("max_eval"), n_random_starts=args.get("random_starts"))
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
        opt_params = out_queue.recv()
        if isinstance(opt_params, Exception):
            abort(404, "failed to get optimization results, err: {}".format(opt_params))
        params = ["%s=%s" % (k, v) for k, v in opt_params["param"].items()]
        result["param"] = ",".join(params)
        result["rank"] = opt_params.get("rank", None)
        result["finished"] = opt_params.get("finished", None)

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
