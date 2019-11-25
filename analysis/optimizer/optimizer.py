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
This class is used to find optimal settings and generate optimized profile.
"""

import numpy as np
from multiprocessing import Process
from skopt.optimizer import gp_minimize
import logging

logger = logging.getLogger(__name__)


class Optimizer(Process):
    def __init__(self, name, params, child_conn, engine = "bayes", max_eval=50):
        super(Optimizer, self).__init__(name=name)
        self.knobs = params
        self.child_conn = child_conn
        self.engine = engine
        self.max_eval = int(max_eval)

    def build_space(self):
        objective_params_list = []
        for p in self.knobs:
            if p['type'] == 'discrete':
                if p['dtype'] == 'int':
                    items = p['items']
                    r = p['range']
                    s = 1
                    if 'step' in p.keys():
                        s = p['step']
                    if r is not None:
                        for i in range(0, len(r), 2):
                            items.extend(list(np.arange(r[i], r[i + 1], step=s)))
                    objective_params_list.append(items)
                if p['dtype'] == 'string':
                    items = p['options']
                    keys = []
                    for i in range(len(items)):
                        keys.append(i)
                    objective_params_list.append(keys)
            elif p['type'] == 'continuous':
                r = p['range']
                objective_params_list.append((r[0], r[1]))
        return objective_params_list

    def run(self):
        def objective(var):
            for i, knob in enumerate(self.knobs):
                params[knob['name']] = var[i]
            print(params)
            self.child_conn.send(params)
            result = self.child_conn.recv()
            x = 0.0
            evalList = result.split(',')
            for value in evalList:
                num = float(value)
                x = x + num
            return x

        ref = []
        params = {}
        for knob in self.knobs:
            ref.append(int(knob['ref']))
        try:
            logger.info("Running performance evaluation.......")
            ret = gp_minimize(objective, self.build_space(), n_calls=self.max_eval)
            logger.info("Minimization procedure has been completed.")
        except ValueError as v:
            logger.error('Value Error:', v)

        for i, knob in enumerate(self.knobs):
            params[knob['name']] = ret.x[i]
        self.child_conn.send(params)
        logger.info("Optimized result: %s" % (params))
        logger.info("The optimized profile has been generated.")
        return params

    def stopProcess(self):
        self.child_conn.close()
        self.terminate()
