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
import multiprocessing
import numpy as np
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler

from analysis.engine.utils import utils
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

    @staticmethod
    def feature_importance(options, performance, labels):
        """feature importance"""
        options = StandardScaler().fit_transform(options)
        lasso = Lasso()
        lasso.fit(options, performance)
        result = zip(lasso.coef_, labels)
        total_sum = sum(map(abs, lasso.coef_))
        if total_sum == 0:
            return ", ".join("%s: 0" % label for label in labels)
        result = sorted(result, key=lambda x: -np.abs(x[0]))
        rank = ", ".join("%s: %s%%" % (label, round(coef * 100 / total_sum, 2))
                         for coef, label in result)
        return rank

    def _get_value_from_knobs(self, kev):
        x_each = []
        for p_nob in self.knobs:
            if p_nob['name'] not in kev.keys():
                raise ValueError("the param {} is not in the x0 ref".format(p_nob['name']))
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
                    raise ValueError("the param format of {} is not correct".format(params))
                kev[params[0]] = params[1]

            ref_x = self._get_value_from_knobs(kev)
            if len(ref_x) != len(self.knobs):
                raise ValueError("tuning parameter is not the same length with knobs")
            list_ref_x.append(ref_x)
        list_ref_y = [float(y) for y in self.y_ref]
        return (list_ref_x, list_ref_y)

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

    def generate_optimizer_param(self, bayes, params, options, performance):
        """generate optimizer paramters"""
        for i, knob in enumerate(self.knobs):
            if bayes['estimator'] is not None:
                params[knob['name']] = bayes['ret'].x[i]
            if self.engine != 'gridsearch':
                bayes['labels'].append(knob['name'])

        LOGGER.info("Optimized result: %s", params)
        LOGGER.info("The optimized profile has been generated.")
        final_param = {}
        if self.sel_feature is True:
            if self.feature_selector == "wefs":
                wefs = WeightedEnsembleFeatureSelector()
                rank = wefs.get_ensemble_feature_importance(options, performance, bayes['labels'])
            elif self.feature_selector == "vrfs":
                vrfs = VarianceReductionFeatureSelector()
                rank = vrfs.get_ensemble_feature_importance(options, performance, bayes['labels'])
            final_param["rank"] = rank
            LOGGER.info("The feature importances of current evaluation are: %s", rank)

        final_param["param"] = params
        final_param["finished"] = True
        self.child_conn.send(final_param)
        return params
