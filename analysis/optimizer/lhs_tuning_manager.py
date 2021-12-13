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
This class is used to perform lhs tuning
"""

import logging

from analysis.optimizer.optimizer import Optimizer

LOGGER = logging.getLogger(__name__)


class LHS(Optimizer):
    """lhs tuning initialize"""

    def __init__(self, name, params, child_conn, prj_name, engine="bayes",
                 max_eval=50, sel_feature=False, x0=None, y0=None,
                 n_random_starts=20, split_count=5, noise=0.00001 ** 2,
                 feature_selector="wefs"):
        super().__init__(name, params, child_conn, prj_name, engine, max_eval,
                         sel_feature, x0, y0, n_random_starts, split_count,
                         noise, feature_selector)

    def run(self):
        """start the tuning process"""
        try:
            from analysis.optimizer.knob_sampling_manager import KnobSamplingManager
            knobsampling_manager = KnobSamplingManager(self.knobs, self.child_conn,
                                                       self.max_eval, self.split_count)
            options = knobsampling_manager.get_knob_samples()
            performance = knobsampling_manager.do_knob_sampling_test(options)
            params = knobsampling_manager.get_best_params(options, performance)
            options = knobsampling_manager.get_options_index(options)
            LOGGER.info("Minimization procedure has been completed.")
        except RuntimeError as runtime_error:
            LOGGER.error('Runtime Error: %s', repr(runtime_error))
            self.child_conn.send(runtime_error)
            return None
        except Exception as err:
            LOGGER.error('Unexpected Error: %s', repr(err))
            self.child_conn.send(Exception("Unexpected Error:", repr(err)))
            return None

        bayes = {'estimator': None, 'ret': None, 'labels': []}
        return self.generate_optimizer_param(bayes, params, options, performance)
