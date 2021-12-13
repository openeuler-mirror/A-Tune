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
# Create: 2021-12-16

"""
This class is used to perform bayes tuning
"""

import collections
import logging
import numbers

from pandas import np
from skopt import Optimizer as baseOpt
from skopt.utils import cook_estimator
from skopt.utils import normalize_dimensions

from analysis.optimizer.optimizer import Optimizer

LOGGER = logging.getLogger(__name__)


class Bayes(Optimizer):
    """bayes tuning initialize"""

    def __init__(self, name, params, child_conn, prj_name, engine="bayes",
                 max_eval=50, sel_feature=False, x0=None, y0=None,
                 n_random_starts=20, split_count=5, noise=0.00001 ** 2,
                 feature_selector="wefs"):
        super().__init__(name, params, child_conn, prj_name, engine, max_eval,
                         sel_feature, x0, y0, n_random_starts, split_count,
                         noise, feature_selector)

    def build_space(self):
        """build space"""
        objective_params_list = []
        for i, p_nob in enumerate(self.knobs):
            if p_nob['type'] == 'discrete':
                items = self.handle_discrete_data(p_nob, i)
                objective_params_list.append(items)
            elif p_nob['type'] == 'continuous':
                r_range = p_nob['range']
                if r_range is None or len(r_range) != 2:
                    raise ValueError("the item of the scope value of {} must be 2"
                                     .format(p_nob['name']))
                if p_nob['dtype'] == 'int':
                    try:
                        r_range[0] = int(r_range[0])
                        r_range[1] = int(r_range[1])
                    except ValueError:
                        raise ValueError("the range value of {} is not an integer value"
                                         .format(p_nob['name']))
                elif p_nob['dtype'] == 'float':
                    try:
                        r_range[0] = float(r_range[0])
                        r_range[1] = float(r_range[1])
                    except ValueError:
                        raise ValueError("the range value of {} is not an float value"
                                         .format(p_nob['name']))

                if len(self.ref) > 0:
                    if self.ref[i] < r_range[0] or self.ref[i] > r_range[1]:
                        raise ValueError("the ref value of {} is out of range"
                                         .format(p_nob['name']))
                objective_params_list.append((r_range[0], r_range[1]))
            else:
                raise ValueError("the type of {} is not supported".format(p_nob['name']))
        return objective_params_list

    def handle_discrete_data(self, p_nob, index):
        """handle discrete data"""
        if p_nob['dtype'] == 'int':
            items = p_nob['items']
            if items is None:
                items = []
            r_range = p_nob['range']
            step = 1
            if 'step' in p_nob.keys():
                step = 1 if p_nob['step'] < 1 else p_nob['step']
            if r_range is not None:
                length = len(r_range) if len(r_range) % 2 == 0 else len(r_range) - 1
                for i in range(0, length, 2):
                    items.extend(list(np.arange(r_range[i], r_range[i + 1] + 1, step=step)))
            items = list(set(items))
            if len(self.ref) > 0:
                try:
                    ref_value = int(self.ref[index])
                except ValueError:
                    raise ValueError("the ref value of {} is not an integer value"
                                     .format(p_nob['name']))
                if ref_value not in items:
                    items.append(ref_value)
            return items
        if p_nob['dtype'] == 'float':
            items = p_nob['items']
            if items is None:
                items = []
            r_range = p_nob['range']
            step = 0.1
            if 'step' in p_nob.keys():
                step = 0.1 if p_nob['step'] <= 0 else p_nob['step']
            if r_range is not None:
                length = len(r_range) if len(r_range) % 2 == 0 else len(r_range) - 1
                for i in range(0, length, 2):
                    items.extend(list(np.arange(r_range[i], r_range[i + 1], step=step)))
            items = list(set(items))
            if len(self.ref) > 0:
                try:
                    ref_value = float(self.ref[index])
                except ValueError:
                    raise ValueError("the ref value of {} is not a float value"
                                     .format(p_nob['name']))
                if ref_value not in items:
                    items.append(ref_value)
            return items
        if p_nob['dtype'] == 'string':
            items = p_nob['options']
            if len(self.ref) > 0:
                try:
                    ref_value = str(self.ref[index])
                except ValueError:
                    raise ValueError("the ref value of {} is not a string value"
                                     .format(p_nob['name']))
                if ref_value not in items:
                    items.append(ref_value)
            return items
        raise ValueError("the dtype of {} is not supported".format(p_nob['name']))

    def run(self):
        """start the tuning process"""

        def objective(var):
            """objective method receive the benchmark result and send the next parameters"""
            iter_result = {}
            option = []
            for i, knob in enumerate(self.knobs):
                params[knob['name']] = var[i]
                if knob['dtype'] == 'string':
                    option.append(knob['options'].index(var[i]))
                else:
                    option.append(var[i])

            iter_result["param"] = params
            self.child_conn.send(iter_result)
            result = self.child_conn.recv()
            x_num = 0.0
            eval_list = result.split(',')
            for value in eval_list:
                num = float(value)
                x_num = x_num + num
            options.append(option)
            performance.append(x_num)
            return x_num

        params = {}
        options = []
        performance = []
        labels = []
        estimator = None

        try:
            params_space = self.build_space()
            ref_x, ref_y = self.transfer()
            if len(ref_x) == 0:
                if len(self.ref) == 0:
                    ref_x = None
                else:
                    ref_x = self.ref
                ref_y = None
            if ref_x is not None and not isinstance(ref_x[0], (list, tuple)):
                ref_x = [ref_x]
            LOGGER.info('x0: %s', ref_x)
            LOGGER.info('y0: %s', ref_y)

            if ref_x is not None and isinstance(ref_x[0], (list, tuple)):
                self._n_random_starts = 0 if len(ref_x) >= self._n_random_starts \
                    else self._n_random_starts - len(ref_x) + 1

            LOGGER.info('n_random_starts parameter is: %d', self._n_random_starts)
            LOGGER.info("Running performance evaluation.......")
            if self.engine == 'random':
                estimator = 'dummy'
            elif self.engine == 'forest':
                estimator = 'RF'
            elif self.engine == 'extraTrees':
                estimator = 'ET'
            elif self.engine == 'gbrt':
                estimator = 'GBRT'
            elif self.engine == 'bayes':
                params_space = normalize_dimensions(params_space)
                estimator = cook_estimator("GP", space=params_space, noise=self.noise)

            LOGGER.info("base_estimator is: %s", estimator)
            optimizer = baseOpt(
                dimensions=params_space,
                n_random_starts=self._n_random_starts,
                random_state=1,
                base_estimator=estimator
            )
            n_calls = self.max_eval
            # User suggested points at which to evaluate the objective first
            if ref_x and ref_y is None:
                ref_y = list(map(objective, ref_x))
                LOGGER.info("ref_y is: %s", ref_y)

            # Pass user suggested initialisation points to the optimizer
            if ref_x:
                if not isinstance(ref_y, (collections.Iterable, numbers.Number)):
                    raise ValueError("`ref_y` should be an iterable or a scalar, "
                                     "got %s" % type(ref_y))
                if len(ref_x) != len(ref_y):
                    raise ValueError("`ref_x` and `ref_y` should "
                                     "have the same length")
                LOGGER.info("ref_x: %s", ref_x)
                LOGGER.info("ref_y: %s", ref_y)
                n_calls -= len(ref_y)
                ret = optimizer.tell(ref_x, ref_y)

            for i in range(n_calls):
                next_x = optimizer.ask()
                LOGGER.info("next_x: %s", next_x)
                LOGGER.info("Running performance evaluation.......")
                next_y = objective(next_x)
                LOGGER.info("next_y: %s", next_y)
                ret = optimizer.tell(next_x, next_y)
                LOGGER.info("finish (ref_x, ref_y) tell")

            LOGGER.info("Minimization procedure has been completed.")
        except ValueError as value_error:
            LOGGER.error('Value Error: %s', repr(value_error))
            self.child_conn.send(value_error)
            return None
        except RuntimeError as runtime_error:
            LOGGER.error('Runtime Error: %s', repr(runtime_error))
            self.child_conn.send(runtime_error)
            return None
        except Exception as err:
            LOGGER.error('Unexpected Error: %s', repr(err))
            self.child_conn.send(Exception("Unexpected Error:", repr(err)))
            return None

        bayes = {'estimator': estimator, 'ret': ret, 'labels': labels}
        return self.generate_optimizer_param(bayes, params, options, performance)
