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
from flask import abort, request
from flask_restful import reqparse, Resource

from analysis.engine.parser import OPTIMIZER_POST_PARSER, OPTIMIZER_PUT_PARSER
from analysis.engine.utils import task_cache, save_data
from analysis.optimizer import optimizer

LOGGER = logging.getLogger(__name__)

PARSER = reqparse.RequestParser()


class Optimizer(Resource):
    """restful api for optimizer, in order to provide the method of post, get, put and delete"""
    task_id_info = "taskid"
    pipe = "pipe"
    _feature_filter_engine = ['random', 'abtest', 'lhs', 'traverse']

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
                abort(404, f"{self.task_id_info} {task_id} not found")
            result.append(task_id)
        return result, 200

    def post(self):
        """provide the method of post"""
        args = OPTIMIZER_POST_PARSER.parse_args()
        LOGGER.info(args)
        task_id = str(uuid.uuid1())
        if args.get("feature_filter") and args.get("engine") not in self._feature_filter_engine:
            abort(400, "feature_filter_engine is not a valid choice, "
                       "only random, abtest, lhs and traverse enabled")
        parent_conn, child_conn = Pipe()
        x_ref = args.get("x_ref")
        y_ref = args.get("y_ref")
        result = {}
        engine = optimizer.Optimizer(task_id, args["knobs"], child_conn, args["prj_name"],
                                     engine=args.get("engine"),
                                     max_eval=args.get("max_eval"),
                                     n_random_starts=args.get("random_starts"),
                                     x0=x_ref, y0=y_ref, split_count=args.get("split_count"),
                                     noise=args.get("noise"),
                                     sel_feature=args.get("feature_filter") or \
                                                 args.get("sel_feature"),
                                     feature_selector=args.get("feature_selector"),
                                     history_path=args.get("history_path"))
        engine.start()

        value = {}
        value["process"] = engine
        value[self.pipe] = parent_conn
        task_cache.TasksCache.get_instance().set(task_id, value)

        iters = args.get("max_eval")
        if args.get("engine") == "abtest" or args.get("engine") == "gridsearch" or \
                args.get("engine") == "traverse":
            iters = parent_conn.recv()
        result["task_id"] = task_id
        result["status"] = "OK"
        result["iters"] = iters
        return result, 200

    def put(self, task_id):
        """provide the method of put"""
        if not task_id:
            abort(404, "task id does not exist")
        task = task_cache.TasksCache.get_instance().get(task_id)
        if not task:
            abort(404, f"taskid {task_id} not found")
        args = OPTIMIZER_PUT_PARSER.parse_args()
        LOGGER.info(args)
        out_queue = task[self.pipe]
        save_data.save_tuning_data(args, out_queue)
        
        if args["iterations"] == -1:
            return {}, 200
        
        result = {}
        opt_params = out_queue.recv()
        if isinstance(opt_params, Exception):
            abort(404, f"failed to get optimization results, err: {opt_params}")
        params = [f"{k}={v}" for k, v in opt_params["param"].items()]
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
            abort(404, f"{self.task_id_info} {task_id} not found")
        process["process"].stop_process()
        task_cache.TasksCache.get_instance().get(task_id)[self.pipe].close()

        task_cache.TasksCache.get_instance().delete(task_id)
        return {}, 200
