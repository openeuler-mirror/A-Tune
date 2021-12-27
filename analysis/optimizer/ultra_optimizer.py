#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2021-12-01

"""
This class is used to perform etpe/smac tuning optimizer with ultraopt lib
(install it: pip3 install ultraopt)
"""

import logging
import sys
from ultraopt.hdl import layering_config, hdl2cs
from ultraopt.optimizer import ETPEOptimizer, ForestOptimizer
from analysis.optimizer.optimizer import Optimizer

LOGGER = logging.getLogger(__name__)

class Ultra(Optimizer):
    """Ultra tuning initialize"""

    def __init__(self, name, params, child_conn, prj_name, engine,
                 max_eval=50, sel_feature=False, x0=None, y0=None,
                 n_random_starts=20, split_count=5, noise=0.00001 ** 2,
                 feature_selector="wefs"):
        super().__init__(name, params, child_conn, prj_name, engine, max_eval,
                         sel_feature, x0, y0, n_random_starts, split_count,
                         noise, feature_selector)

    def run(self):
        """start the tuning process"""
        try:
            ultra_opt = UltraOptimizer(
                self.engine, self.knobs, self.child_conn, self.max_eval)
            best_params = ultra_opt.ultra_minimize_tuning()
            final_param = {"finished": True, "param": best_params}
            self.child_conn.send(final_param)
            return best_params
        except RuntimeError as runtime_error:
            LOGGER.error('Runtime Error: %s', repr(runtime_error))
            self.child_conn.send(runtime_error)
            return None
        except Exception as err:
            LOGGER.error('Unexpected Error: %s', repr(err))
            self.child_conn.send(Exception("Unexpected Error:", repr(err)))
            return None


class UltraOptimizer:
    """Ultra tuning manager"""

    def __init__(self, alg_name, knobs, child_conn, max_eval=100):
        self._search_space = {}
        self._alg_name = alg_name
        self._knobs = knobs
        self._child_conn = child_conn
        self._max_eval = max_eval
        self.define_search_space(knobs)

    def define_search_space(self, knobs):
        """define the search space of etpe/smac tuning algorithms"""
        self._search_space = {}
        for p_nob in knobs:
            if p_nob['type'] == 'discrete':
                if p_nob['dtype'] == 'string':
                    _type = "choice"
                    _value = p_nob['options']
                elif p_nob['dtype'] == 'int' or p_nob['dtype'] == 'float':
                    if p_nob['items'] is not None:
                        _type = "choice"
                        _value = p_nob['items']
                    else:
                        if 'step' in p_nob.keys():
                            if p_nob['dtype'] == 'int':
                                step = 1 if p_nob['step'] < 1 else p_nob['step']
                            elif p_nob['dtype'] == 'float':
                                step = 0.1 if p_nob['step'] <= 0 else p_nob['step']

                        if p_nob['dtype'] == 'int':
                            _type = "int_quniform"
                            _value = [p_nob['range'][0],
                                      p_nob['range'][1], step]
                        else:
                            _type = "quniform"
                            _value = [p_nob['range'][0],
                                      p_nob['range'][1], step]
            else:
                _type = "uniform"
                _value = [p_nob['range'][0], p_nob['range'][1]]

            self._search_space[p_nob['name']] = {
                "_type": _type, "_value": _value}

    def ultra_minimize_tuning(self):
        """runing the tpe/smac tuning algorithm"""

        def evaluate(config):
            """evalute the performance at each iteration"""
            
            iter_result = {}

            iter_result["param"] = layering_config(config)
            self._child_conn.send(iter_result)
            result = self._child_conn.recv()
            x_num = 0.0
            eval_list = result.split(',')
            for value in eval_list:
                num = float(value)
                x_num = x_num + num
            performance = x_num
            LOGGER.info('%s tuning: %s, result: %s',
                        self._alg_name, config, performance)
            return performance / 1000.0

        if self._alg_name == "etpe":
            optimizer = ETPEOptimizer()
        if self._alg_name == "smac":
            optimizer = ForestOptimizer()
        search_space = hdl2cs(self._search_space)

        optimizer.initialize(search_space)
        best_loss = sys.maxsize - 1
        best_config = None

        for _ in range(self._max_eval):
            recommend_config, config_info = optimizer.ask()
            loss = evaluate(recommend_config)
            optimizer.tell(recommend_config, loss)
            if loss < best_loss:
                best_loss = loss
                best_config = recommend_config

        return best_config
