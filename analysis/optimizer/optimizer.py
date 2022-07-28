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
This class is used to find optimal settings and generate optimized profile.
"""

import logging
import numbers
import random
import multiprocessing
import collections
import numpy as np
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler

from skopt import Optimizer as baseOpt
from skopt.utils import normalize_dimensions
from skopt.utils import cook_estimator

from analysis.engine.utils import utils
from analysis.optimizer.abtest_tuning_manager import ABtestTuningManager
from analysis.optimizer.gridsearch_tuning_manager import GridSearchTuningManager
from analysis.optimizer.weighted_ensemble_feature_selector import WeightedEnsembleFeatureSelector
from analysis.optimizer.variance_reduction_feature_selector import VarianceReductionFeatureSelector


LOGGER = logging.getLogger(__name__)


class Optimizer(multiprocessing.Process):
    """find optimal settings and generate optimized profile"""

    def __init__(self, name, params, child_conn, prj_name, engine="bayes",
                 max_eval=50, sel_feature=False, x0=None, y0=None,
                 n_random_starts=20, split_count=5, noise=0.00001 ** 2, feature_selector="wefs"):
        super().__init__(name=name)
        self.knobs = self.check_multiple_params(params)
        self.child_conn = child_conn
        self.project_name = prj_name
        self.engine = engine
        self.noise = noise
        self.max_eval = int(max_eval)
        self.split_count = split_count
        self.sel_feature = sel_feature
        self.x_ref = x0
        self.y_ref = y0
        if self.x_ref is not None and len(self.x_ref) == 1:
            ref_x, _ = self.transfer()
            self.ref = ref_x[0]
        else:
            self.ref = []
        self._n_random_starts = 20 if n_random_starts is None else n_random_starts
        self.feature_selector = feature_selector

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
                    raise ValueError(f"the item of the scope value of {p_nob['name']} must be 2")
                if p_nob['dtype'] == 'int':
                    try:
                        r_range[0] = int(r_range[0])
                        r_range[1] = int(r_range[1])
                    except ValueError as e:
                        raise ValueError(f"the range value of {p_nob['name']} is not an integer value") from e
                elif p_nob['dtype'] == 'float':
                    try:
                        r_range[0] = float(r_range[0])
                        r_range[1] = float(r_range[1])
                    except ValueError as e:
                        raise ValueError(f"the range value of {p_nob['name']} is not an float value") from e

                if len(self.ref) > 0:
                    if self.ref[i] < r_range[0] or self.ref[i] > r_range[1]:
                        raise ValueError(f"the ref value of {p_nob['name']} is out of range")
                objective_params_list.append((r_range[0], r_range[1]))
            else:
                raise ValueError(f"the type of {p_nob['name']} is not supported")
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
                except ValueError as e:
                    raise ValueError(f"the ref value of {p_nob['name']} is not an integer value") from e
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
                except ValueError as e:
                    raise ValueError(f"the ref value of {p_nob['name']} is not a float value") from e
                if ref_value not in items:
                    items.append(ref_value)
            return items
        if p_nob['dtype'] == 'string':
            items = p_nob['options']
            if len(self.ref) > 0:
                try:
                    ref_value = str(self.ref[index])
                except ValueError as e:
                    raise ValueError(f"the ref value of {p_nob['name']} is not a string value") from e
                if ref_value not in items:
                    items.append(ref_value)
            return items
        raise ValueError(f"the dtype of {p_nob['name']} is not supported")

    @staticmethod
    def feature_importance(options, performance, labels):
        """feature importance"""
        options = StandardScaler().fit_transform(options)
        lasso = Lasso()
        lasso.fit(options, performance)
        result = zip(lasso.coef_, labels)
        total_sum = sum(map(abs, lasso.coef_))
        if total_sum == 0:
            return ", ".join(f"{label}: 0" for label in labels)
        result = sorted(result, key=lambda x: -np.abs(x[0]))
        rank = ", ".join(f"{label}: {round(coef * 100 / total_sum, 2)}%%"
                         for coef, label in result)
        return rank

    def _get_value_from_knobs(self, kev):
        x_each = []
        for p_nob in self.knobs:
            if p_nob['name'] not in kev.keys():
                raise ValueError(f"the param {p_nob['name']} is not in the x0 ref")
            if p_nob['dtype'] == 'int':
                x_each.append(int(kev[p_nob['name']]))
            elif p_nob['dtype'] == 'float':
                x_each.append(float(kev[p_nob['name']]))
            else:
                x_each.append(kev[p_nob['name']])
        return x_each

    def transfer(self):
        """transfer ref x0 to int, y0 to float"""
        list_ref_x = []
        list_ref_y = []
        if self.x_ref is None or self.y_ref is None:
            return (list_ref_x, list_ref_y)

        for x_value in self.x_ref:
            kev = {}
            if len(x_value) != len(self.knobs):
                raise ValueError("x0 is not the same length with knobs")

            for val in x_value:
                params = val.split("=")
                if len(params) != 2:
                    raise ValueError(f"the param format of {params} is not correct")
                kev[params[0]] = params[1]

            ref_x = self._get_value_from_knobs(kev)
            if len(ref_x) != len(self.knobs):
                raise ValueError("tuning parameter is not the same length with knobs")
            list_ref_x.append(ref_x)
        list_ref_y = [float(y) for y in self.y_ref]
        return (list_ref_x, list_ref_y)

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
            if self.engine == 'random' or self.engine == 'forest' or \
                    self.engine == 'gbrt' or self.engine == 'bayes' or self.engine == 'extraTrees':
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
                    random_state=random.randint(0, 1000),
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
                        raise ValueError(f"`ref_y` should be an iterable or a scalar, got {type(ref_y)}")
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

            elif self.engine == 'abtest':
                abtuning_manager = ABtestTuningManager(self.knobs, self.child_conn,
                                                       self.split_count)
                options, performance = abtuning_manager.do_abtest_tuning_abtest()
                params = abtuning_manager.get_best_params()
                # convert string option into index
                options = abtuning_manager.get_options_index(options)
            elif self.engine == 'gridsearch':
                num_done = 0
                if self.y_ref is not None:
                    num_done = len(self.y_ref)
                gstuning_manager = GridSearchTuningManager(self.knobs, self.child_conn)
                options, performance = gstuning_manager.do_gridsearch(num_done)
                params, labels = gstuning_manager.get_best_params()
                # convert string option into index
                options = gstuning_manager.get_options_index(options)
            elif self.engine == 'GA':
                from analysis.optimizer.gatuning_manager import GATuning
                gatuning_manager = GATuning(self.knobs,self.child_conn)
                params = gatuning_manager.GA()
            elif self.engine == 'lhs':
                from analysis.optimizer.knob_sampling_manager import KnobSamplingManager
                knobsampling_manager = KnobSamplingManager(self.knobs, self.child_conn,
                                                           self.max_eval, self.split_count)
                options = knobsampling_manager.get_knob_samples()
                performance = knobsampling_manager.do_knob_sampling_test(options)
                params = knobsampling_manager.get_best_params(options, performance)
                options = knobsampling_manager.get_options_index(options)
            elif self.engine == 'tpe':
                from analysis.optimizer.tpe_optimizer import TPEOptimizer
                tpe_opt = TPEOptimizer(self.knobs, self.child_conn, self.max_eval)
                best_params = tpe_opt.tpe_minimize_tuning()
                final_param = {}
                final_param["finished"] = True
                final_param["param"] = best_params
                self.child_conn.send(final_param)
                return best_params
            elif self.engine == 'traverse':
                from analysis.optimizer.knob_traverse_manager import KnobTraverseManager
                default_values = [p_nob['ref'] for _, p_nob in enumerate(self.knobs)]
                knobtraverse_manager = KnobTraverseManager(self.knobs, self.child_conn,
                                                           default_values)
                traverse_list = knobtraverse_manager.get_traverse_list()
                performance = knobtraverse_manager.get_traverse_performance(traverse_list)
                rank = knobtraverse_manager.get_traverse_rank(performance)
                final_param = {"rank": rank, "param": knobtraverse_manager.get_default_values(),
                               "finished": True}
                self.child_conn.send(final_param)
                return final_param["param"]

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

        for i, knob in enumerate(self.knobs):
            if estimator is not None:
                params[knob['name']] = ret.x[i]
            if self.engine != 'gridsearch':
                labels.append(knob['name'])

        LOGGER.info("Optimized result: %s", params)
        LOGGER.info("The optimized profile has been generated.")
        final_param = {}
        if self.sel_feature is True:
            if self.feature_selector == "wefs":
                wefs = WeightedEnsembleFeatureSelector()
                rank = wefs.get_ensemble_feature_importance(options, performance, labels)
            elif self.feature_selector == "vrfs":
                vrfs = VarianceReductionFeatureSelector()
                rank = vrfs.get_ensemble_feature_importance(options, performance, labels)
            final_param["rank"] = rank
            LOGGER.info("The feature importances of current evaluation are: %s", rank)

        final_param["param"] = params
        final_param["finished"] = True
        self.child_conn.send(final_param)
        return params

    def stop_process(self):
        """stop process"""
        self.child_conn.close()
        self.terminate()

    @staticmethod
    def check_multiple_params(params):
        """check multiple params"""
        for ind, param in enumerate(params):
            if param["options"] is None and param['dtype'] == 'string':
                params[ind] = utils.get_tuning_options(param)
        return params
