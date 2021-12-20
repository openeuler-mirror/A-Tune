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
This class is used to perform traverse tuning
"""

import logging

from analysis.optimizer.optimizer import Optimizer

LOGGER = logging.getLogger(__name__)


class Traverse(Optimizer):
    """traverse tuning initialize"""

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
            from analysis.optimizer.knob_traverse_manager import KnobTraverseManager
            default_values = [p_nob['ref'] for _, p_nob in enumerate(self.knobs)]
            knobtraverse_manager = KnobTraverseManager(self.knobs, self.child_conn, default_values)
            traverse_list = knobtraverse_manager.get_traverse_list()
            performance = knobtraverse_manager.get_traverse_performance(traverse_list)
            rank = knobtraverse_manager.get_traverse_rank(performance)
            final_param = {"rank": rank, "param": knobtraverse_manager.get_default_values(), "finished": True}
            self.child_conn.send(final_param)
            return final_param["param"]
        except RuntimeError as runtime_error:
            LOGGER.error('Runtime Error: %s', repr(runtime_error))
            self.child_conn.send(runtime_error)
            return None
        except Exception as err:
            LOGGER.error('Unexpected Error: %s', repr(err))
            self.child_conn.send(Exception("Unexpected Error:", repr(err)))
            return None
