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
# Create: 2020-8-02

"""
This class is used to perform tpe tuning optimizer with hyperopt lib
(install it: pip3 install hyperopt)
"""

import logging
import numpy as np
from hyperopt import fmin, tpe, space_eval, hp

LOGGER = logging.getLogger(__name__)


class TPEDiscreteKnob:
    """tpe tuning space generator"""

    def __init__(self, p_nob):
        option_range = []
        if p_nob['dtype'] == 'string':
            option_range.extend(p_nob['options'])
        elif p_nob['dtype'] == 'int' or p_nob['dtype'] == 'float':
            items = p_nob['items']
            if items is not None:
                for item in items:
                    option_range.append(item)

            step = 1
            if 'step' in p_nob.keys():
                if p_nob['dtype'] == 'int':
                    step = 1 if p_nob['step'] < 1 else p_nob['step']
                elif p_nob['dtype'] == 'float':
                    step = 0.1 if p_nob['step'] <= 0 else p_nob['step']

            if p_nob['range'] is not None:
                for val in np.arange(p_nob['range'][0], p_nob['range'][1], step):
                    option_range.append(val)
        self.option_choice = hp.choice(p_nob['name'], option_range)


class TPEOptimizer:
    """tpe tuning manager"""

    def __init__(self, knobs, child_conn, max_eval=100):
        self._search_space = {}
        for p_nob in knobs:
            if p_nob['type'] == 'discrete':
                tpe_knob = TPEDiscreteKnob(p_nob)
                self._search_space[p_nob['name']] = tpe_knob.option_choice
            elif p_nob['type'] == 'continuous':
                self._search_space[p_nob['name']] = hp.uniform(p_nob['name'], p_nob['range'][0],
                                                               p_nob['range'][1])
        self._knobs = knobs
        self._child_conn = child_conn
        self._max_eval = max_eval

    def tpe_minimize_tuning(self):
        """runing the tpe tuning algorithm"""

        def test_performance(args):
            """generate the params and send to client to run benchmark"""
            iter_result = {}
            params = {}
            for p_nob in self._knobs:
                knob_name = p_nob['name']
                knob_val = args[knob_name]
                if p_nob['dtype'] == 'int':
                    params[knob_name] = int(knob_val)
                else:
                    params[knob_name] = knob_val
            iter_result["param"] = params
            self._child_conn.send(iter_result)
            result = self._child_conn.recv()
            x_num = 0.0
            eval_list = result.split(',')
            for value in eval_list:
                num = float(value)
                x_num = x_num + num
            performance = x_num
            LOGGER.info('tpe tuning: %s, result: %s', args, performance)
            return performance

        best = fmin(
            test_performance,
            self._search_space,
            algo=tpe.suggest,
            max_evals=self._max_eval
        )
        best_val = space_eval(self._search_space, best)
        return best_val
