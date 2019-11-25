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
from flask import Flask, abort
from flask import current_app
from flask_restful import reqparse, Resource
from flask_restful import request, marshal_with, marshal_with_field
import os
import uuid
from multiprocessing import Queue, Pipe

import resources.optimizer
from resources.field import optimizer_post_field
from resources.parser import optimizer_post_parser
from resources.parser import optimizer_put_parser
from optimizer import optimizer
from utils import task_cache
import logging

logger = logging.getLogger(__name__)

parser = reqparse.RequestParser()


class Optimizer(Resource):
    def get(self, task_id=None):
        result = []
        if not task_id:
            tasks_all = task_cache.TasksCache.getInstance().get_all()
            for task in tasks_all:
                result.append(task)
        else:
            task = task_cache.TasksCache.getInstance().get(task_id)
            if not task:
                abort(404, "taskid {0} not found".format(task_id))
            result.append(task_id)
        return result, 200

    # @marshal_with_field(optimizdder_post_field)
    def post(self):
        args = optimizer_post_parser.parse_args()
        logger.info(args)

        if args["max_eval"] < 10:
            abort(400, "max_eval must be >=10")
        task_id = str(uuid.uuid1())

        parent_conn, child_conn = Pipe()
        engine = optimizer.Optimizer(task_id, args["knobs"], child_conn, max_eval=args.get("max_eval"))
        engine.start()

        value = {}
        value["process"] = engine
        value["pipe"] = parent_conn
        task_cache.TasksCache.getInstance().set(task_id, value)

        result = {}

        result["task_id"] = task_id
        return result, 201

    def put(self, task_id):
        if not task_id:
            abort(404)
        task = task_cache.TasksCache.getInstance().get(task_id)
        if not task:
            abort(404, "taskid {0} not found".format(task_id))

        args = optimizer_put_parser.parse_args()
        logger.info(args)
        out_queue = task["pipe"]
        if args["iterations"] != 0:
            out_queue.send(args.get("value"))

        result = {}
        values = out_queue.recv()
        params = ["%s=%s" % (k, v) for k, v in values.items()]
        result["param"] = ",".join(params)

        return result, 200

    def delete(self, task_id):
        if not task_id:
            abort(404)
        process = task_cache.TasksCache.getInstance().get(task_id)
        if not process:
            abort(404, "taskid {0} not found".format(task_id))
        process["process"].stopProcess()
        task_cache.TasksCache.getInstance().get(task_id)["pipe"].close()

        process = task_cache.TasksCache.getInstance().delete(task_id)
        return {}, 200
        
