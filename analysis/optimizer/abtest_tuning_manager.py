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
# Create: 2020-07-30

"""
This class is used to perform white box tuning and generate optimized profile
"""

import logging
import numpy as np

LOGGER = logging.getLogger(__name__)


class ABtestTuning:
    """abtest tuning"""

    def __init__(self, p_nob, split_count=5):
        items = []
        if p_nob['dtype'] == 'string':
            items.extend(p_nob['options'])
        elif p_nob['dtype'] == 'int' or p_nob['dtype'] == 'float':
            p_items = p_nob['items']
            if p_items is not None:
                for item in p_items:
                    items.append(str(item))
            step = 1
            if p_nob['range'] is not None:
                if 'step' in p_nob.keys():
                    if p_nob['dtype'] == 'int':
                        step = int((p_nob['range'][1] - p_nob['range'][0]) / split_count)
                    elif p_nob['dtype'] == 'float':
                        step = float((p_nob['range'][1] - p_nob['range'][0]) / split_count)
                item_val = p_nob['range'][0]
                for _ in range(split_count):
                    items.append(str(item_val))
                    item_val += step
        self.items = items


class ABtestTuningManager:
    """abtest tuning manager"""

    def __init__(self, knobs, child_conn, split_count):
        abtuning_list = []
        name_list = []
        for p_nob in knobs:
            abtuning = ABtestTuning(p_nob, split_count)
            abtuning_list.append(abtuning)
            name_list.append(p_nob['name'])
        self._abtuning_list = abtuning_list
        self._name_list = name_list
        self._child_conn = child_conn
        self._knobs = knobs
        self._abtuning_num = len(self._abtuning_list)
        self._abtuning_index = 0
        self._default_val_vec = []
        self._best_val_vec = []
        self._performance = []
        self._options = []
        self._max_eval = 0
        for i in range(self._abtuning_num):
            self._max_eval += len(self._abtuning_list[i].items)
            self._default_val_vec.append(self._abtuning_list[i].items[0])
            self._best_val_vec.append(self._abtuning_list[i].items[0])
        self._child_conn.send(self._max_eval)

    def construct_set_knob_val_vec(self, item):
        """construct set knob val vec"""
        index = self._abtuning_index
        set_knob_val_vec = []
        for i in range(index):
            set_knob_val_vec.append(self._best_val_vec[i])
        set_knob_val_vec.append(item)
        for i in range(index + 1, self._abtuning_num):
            set_knob_val_vec.append(self._default_val_vec[i])
        return set_knob_val_vec

    def test_performance_one_abtuning_item(self, item):
        """test performance of one abtuning item"""
        set_knob_val_vec = self.construct_set_knob_val_vec(item)
        self._options.append(set_knob_val_vec)
        iter_result = {}
        params = {}
        for i, val in enumerate(set_knob_val_vec):
            knob_val = val
            knob_name = self._name_list[i]
            if self._knobs[i]['dtype'] == 'int':
                params[knob_name] = int(knob_val)
            elif self._knobs[i]['dtype'] == 'float':
                params[knob_name] = float(knob_val)
            elif self._knobs[i]['dtype'] == 'string':
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
        return performance

    def do_one_abtest_tuning(self):
        """do one abtest tuning"""
        index = self._abtuning_index
        abtuning = self._abtuning_list[index]
        LOGGER.info('In %s tuning: %s', self._name_list[index], abtuning.items)
        results = []
        for item in abtuning.items:
            result = self.test_performance_one_abtuning_item(item)
            self._performance.append(result)
            results.append(result)
            LOGGER.info('  -with item %s, result: %s', item, result)
        np_results = np.array(results)
        best_index = np.argmin(np_results)
        best_abtest_item = abtuning.items[best_index]
        self._best_val_vec[index] = best_abtest_item
        LOGGER.info('  -Get best item: %s, best result: %s', best_abtest_item, results[best_index])
        LOGGER.info('==== ==== End %s tuning ==== ====', self._name_list[index])

    def do_abtest_tuning_abtest(self):
        """do abtest tuning abtest"""
        self._abtuning_index = 0
        while self._abtuning_index < self._abtuning_num:
            self.do_one_abtest_tuning()
            self._abtuning_index += 1
        return self._options, self._performance

    def get_best_params(self):
        """return the parameters of the best performance"""
        params = {}
        best_index = np.argmin(self._performance)
        best_option = self._options[best_index]
        for i, val in enumerate(best_option):
            knob_val = val
            knob_name = self._name_list[i]
            if self._knobs[i]['dtype'] == 'int':
                params[knob_name] = int(knob_val)
            elif self._knobs[i]['dtype'] == 'float':
                params[knob_name] = float(knob_val)
            elif self._knobs[i]['dtype'] == 'string':
                params[knob_name] = knob_val
        return params

    def get_option_index(self, option):
        """return the index of the option list"""
        option_range_list = self._abtuning_list
        option_index = []
        for i, val in enumerate(option):
            index = option_range_list[i].items.index(val)
            option_index.append(index)
        return option_index

    def get_options_index(self, options):
        """return the options index of the options"""
        options_index = []
        for option in options:
            option_index = self.get_option_index(option)
            options_index.append(option_index)
        return options_index
