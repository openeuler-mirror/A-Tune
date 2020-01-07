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

import logging
from multiprocessing import Process
import numpy as np
from skopt.optimizer import gp_minimize

LOGGER = logging.getLogger(__name__)


class Optimizer(Process):
    """find optimal settings and generate optimized profile"""

    def __init__(self, name, params, child_conn, engine="bayes", max_eval=50):
        super(Optimizer, self).__init__(name=name)
        self.knobs = params
        self.child_conn = child_conn
        self.engine = engine
        self.max_eval = int(max_eval)

    def build_space(self):
        """build space"""
        objective_params_list = []
        for p_nob in self.knobs:
            if p_nob['type'] == 'discrete':
                if p_nob['dtype'] == 'int':
                    items = p_nob['items']
                    if items is None:
                        items = []
                    r_range = p_nob['range']
                    step = 1
                    if 'step' in p_nob.keys():
                        step = p_nob['step']
                    if r_range is not None:
                        for i in range(0, len(r_range), 2):
                            items.extend(list(np.arange(r_range[i], r_range[i + 1], step=step)))
                    items = list(set(items))
                    objective_params_list.append(items)
                if p_nob['dtype'] == 'string':
                    items = p_nob['options']
                    keys = []
                    for i in range(len(items)):
                        keys.append(i)
                    objective_params_list.append(keys)
            elif p_nob['type'] == 'continuous':
                r_range = p_nob['range']
                objective_params_list.append((r_range[0], r_range[1]))
        return objective_params_list

    def run(self):
        def objective(var):
            for i, knob in enumerate(self.knobs):
                if knob['dtype'] == 'string':
                    params[knob['name']] = knob['options'][var[i]]
                else:
                    params[knob['name']] = var[i]
            self.child_conn.send(params)
            result = self.child_conn.recv()
            x_num = 0.0
            eval_list = result.split(',')
            for value in eval_list:
                num = float(value)
                x_num = x_num + num
            return x_num

        params = {}
        ref = []
        for knob in self.knobs:
            if knob['dtype'] == 'string':
                for key, value in enumerate(knob['options']):
                    if knob['ref'] == value:
                        ref.append(key)
            else:
                ref.append(int(knob['ref']))
        try:
            LOGGER.info("Running performance evaluation.......")
            ret = gp_minimize(objective, self.build_space(), n_calls=self.max_eval, x0=ref)
            LOGGER.info("Minimization procedure has been completed.")
        except ValueError as value_error:
            LOGGER.error('Value Error: %s', value_error)

        for i, knob in enumerate(self.knobs):
            if knob['dtype'] == 'string':
                params[knob['name']] = knob['options'][ret.x[i]]
            else:
                params[knob['name']] = ret.x[i]
        self.child_conn.send(params)
        LOGGER.info("Optimized result: %s", params)
        LOGGER.info("The optimized profile has been generated.")
        return params

    def stop_process(self):
        """stop process"""
        self.child_conn.close()
        self.terminate()
