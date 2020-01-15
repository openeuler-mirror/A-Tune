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
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler

LOGGER = logging.getLogger(__name__)


class Optimizer(Process):
    """find optimal settings and generate optimized profile"""

    def __init__(self, name, params, child_conn, engine="bayes", max_eval=50):
        super(Optimizer, self).__init__(name=name)
        self.knobs = params
        self.child_conn = child_conn
        self.engine = engine
        self.max_eval = int(max_eval)
        self.ref = []

    def build_space(self):
        """build space"""
        objective_params_list = []
        for p_nob in self.knobs:
            if p_nob['type'] == 'discrete':
                items = self.handle_discrete_data(p_nob)
                objective_params_list.append(items)
            elif p_nob['type'] == 'continuous':
                r_range = p_nob['range']
                if int(p_nob['ref']) < int(r_range[0]) or int(p_nob['ref']) > int(r_range[1]):
                    raise ValueError("the default value of {} is out of range"
                                     .format(p_nob['name']))
                self.ref.append(int(p_nob['ref']))
                objective_params_list.append((r_range[0], r_range[1]))
            else:
                raise ValueError("the type of {} is not supported".format(p_nob['name']))
        return objective_params_list

    def handle_discrete_data(self, p_nob):
        """handle discrete data"""
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
                    items.extend(list(np.arange(r_range[i], r_range[i + 1] + 1, step=step)))
            items = list(set(items))
            if int(p_nob['ref']) not in items:
                raise ValueError("the default value of {} is out of range"
                                 .format(p_nob['name']))
            self.ref.append(int(p_nob['ref']))
            return items
        if p_nob['dtype'] == 'string':
            items = p_nob['options']
            keys = []
            length = len(self.ref)
            for key, value in enumerate(items):
                keys.append(key)
                if p_nob['ref'] == value:
                    self.ref.append(key)
            if len(self.ref) == length:
                raise ValueError("the default value of {} is out of range"
                                 .format(p_nob['name']))
            return keys
        raise ValueError("the dtype of {} is not supported".format(p_nob['name']))

    @staticmethod
    def feature_importance(options, performance, labels):
        """feature importance"""
        options = StandardScaler().fit_transform(options)
        lasso = Lasso()
        lasso.fit(options, performance)
        result = zip(lasso.coef_, labels)
        result = sorted(result, key=lambda x: -np.abs(x[0]))
        rank = ", ".join("%s: %s" % (label, round(coef, 3))for coef, label in result)
        return rank

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
        options = []
        performance = []
        labels = []
        try:
            LOGGER.info("Running performance evaluation.......")
            ret = gp_minimize(objective, self.build_space(), n_calls=self.max_eval, x0=self.ref)
            LOGGER.info("Minimization procedure has been completed.")
        except ValueError as value_error:
            LOGGER.error('Value Error: %s', value_error)
            self.child_conn.send(value_error)
            return None

        for i, knob in enumerate(self.knobs):
            if knob['dtype'] == 'string':
                params[knob['name']] = knob['options'][ret.x[i]]
            else:
                params[knob['name']] = ret.x[i]
            labels.append(knob['name'])
        self.child_conn.send(params)
        LOGGER.info("Optimized result: %s", params)
        LOGGER.info("The optimized profile has been generated.")

        rank = self.feature_importance(options, performance, labels)
        LOGGER.info("The feature importances of current evaluation are: %s", rank)
        return params

    def stop_process(self):
        """stop process"""
        self.child_conn.close()
        self.terminate()
