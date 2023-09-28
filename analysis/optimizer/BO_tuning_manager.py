#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2023-09-26

"""
This class is used to perform bayesian optimization for tuning with transfer learning
"""


import logging
from typing import List, Dict

from openbox import Advisor, History, Observation

from analysis.default_config import TUNING_DATA_PATH
from typing import List

from openbox import space as sp, History
from ConfigSpace import Configuration

LOGGER = logging.getLogger(__name__)


def knobs2config(knobs):
    """
    transform knob to config_space  defined in openbox
    """
    config_space = sp.Space()
    variables = []
    for knob in knobs:
        if knob['dtype'] == 'int':
            variables.append(sp.Int(knob['name'], lower=knob['range'][0], upper=knob['range'][1]))
        elif knob['dtype'] == 'string':
            variables.append(sp.Categorical(knob['name'], choices=knob['options']))
    config_space.add_variables(variables)
    return config_space


def config2param(config: Configuration):
    """
    transform configSpace to dict
    """
    config_dict = config.get_dictionary()
    return {'param': config_dict}


def load_history(histories, config_space) -> List[History]:
    """
    load tuning history from files
    """
    transfer_learning_history = list()  # type: List[History]
    for history_task_location in histories:
        history = History.load_json(history_task_location, config_space)
        transfer_learning_history.append(history)
    return transfer_learning_history




class BO_Optimizer:
    """
     Bayesian optimization for hyperparameter tuning
     if transfer is true: Perform Bayesian optimization with RGPE to transfer historical tuning knowledge.
     else: Perform naive gaussian process based Bayesian optimization

     *** add history path in yaml files: history_path: [/var/atune_data/tuning/finished/xxxx.json, /var/atune_data/tuning/finished/xxxx.json]
    """

    def __init__(self, knobs, child_conn, max_eval, prj_name="bo-optimizer-test-TL",
                 history_path=None) -> None:

        self._child_conn = child_conn
        self._max_eval = max_eval
        self._knobs = knobs
        self.prj_name = prj_name
        self.config_space = knobs2config(knobs)
        self.transfer = False
        LOGGER.info("history path {}".format(history_path))
        if history_path is None:
            history_path = []
        else:
            if len(history_path) > 0:
                LOGGER.info("Load tuning history from {}".format(history_path))
                self.transfer_learning_history = load_history(history_path, self.config_space)
                self.transfer = True

        if self.transfer:
            self.bo_optimizer = Advisor(
                config_space=self.config_space,
                num_objectives=1,
                num_constraints=0,
                initial_trials=5,
                transfer_learning_history=self.transfer_learning_history,  # type: List[History]
                surrogate_type='tlbo_rgpe_gp',
                acq_type='auto',
                task_id=prj_name,
            )
        else:
            self.bo_optimizer = Advisor(
                config_space=self.config_space,
                num_objectives=1,
                num_constraints=0,
                initial_trials=5,
                surrogate_type='gp',
                acq_type='auto',
                task_id=prj_name,
            )

    def objective(self, config):
        param = config2param(config)
        self._child_conn.send(param)
        result = self._child_conn.recv()
        obj = 0.0
        eval_list = result.split(',')
        for value in eval_list:
            obj += -1.0 * float(value)
        return obj, param

    def run(self) -> Dict[str, dict]:
        """Run optimization with bayesian optimization
        Returns:
            dict[str, dict]: best parameters of the tuned system
        """
        best_params = None
        max_obj = 0.
        for i in range(self._max_eval):
            config = self.bo_optimizer.get_suggestion()
            obj, param = self.objective(config)
            observation = Observation(config=config, objectives=[-obj])
            self.bo_optimizer.update_observation(observation)
            if obj > max_obj:
                best_params = param
        self.bo_optimizer.history.save_json(TUNING_DATA_PATH + 'finished' + '/' + 'bo_' + self.prj_name + ".json")
        return best_params
