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
This class is used to perform gridsearch tuning and generate optimized profile
"""

import logging
import copy
import numpy as np

LOGGER = logging.getLogger(__name__)


class GridSearchTuning:
    """gridsearch tuning"""

    def __init__(self, p_nob):
        items = []
        r_range = p_nob['range']
        if p_nob['dtype'] == 'string':
            items.extend(p_nob['options'])
        elif p_nob['dtype'] == 'int' or p_nob['dtype'] == 'float':
            p_items = p_nob['items']
            if p_items is not None:
                for item in p_items:
                    items.append(str(item))
            step = 1
            if 'step' in p_nob.keys():
                step = 1 if p_nob['step'] < 1 else p_nob['step']
            if r_range is not None:
                length = len(r_range) if len(r_range) % 2 == 0 else len(r_range) - 1
                for i in range(0, length, 2):
                    items.extend(list(np.arange(r_range[i], r_range[i + 1] + 1, step=step)))
                items = list(set(items))
        self.items = items


class GridSearchTuningManager:
    """gridsearch tuning manager"""

    def __init__(self, knobs, child_conn):
        option_list = {}
        dict_para = {}
        dict_para_type = {}
        for p_nob in knobs:
            gstuning = GridSearchTuning(p_nob)
            option_list[p_nob['name']] = gstuning
            dict_para[p_nob['name']] = gstuning.items
            dict_para_type[p_nob['name']] = p_nob['dtype']

        self._dict_para = dict_para
        self._dict_para_type = dict_para_type
        self._name = []
        self._option_list = option_list
        self._options = []
        self._performance = []
        self._child_conn = child_conn

    def expand_parameters(self, para):
        """return the expand tuning parameter combinations"""
        if len(para) == 1:
            for key, values in para.items():
                return list(map(lambda v: {key: v}, values))

        key = list(para)[0]
        values = para.pop(key)
        rest_para = self.expand_parameters(para)
        ret_para = list()
        for val in values:
            for config in rest_para:
                config[key] = val
                ret_para.append(copy.deepcopy(config))
        return ret_para

    def do_gridsearch(self, num_done):
        """do the gridsearch on the spaces"""
        spaces = self.expand_parameters(self._dict_para)
        self._child_conn.send(len(spaces))
        for space in spaces[num_done:]:
            LOGGER.info('space %s', space)
            iter_result = {}
            params = {}
            option = []
            name = []
            for key in space:
                option.append(space[key])
                name.append(key)
                LOGGER.info('key: %s,  value: %s, type: %s', key,
                            space[key], self._dict_para_type[key])
                if self._dict_para_type[key] == 'int':
                    params[key] = int(space[key])
                elif self._dict_para_type[key] == 'float':
                    params[key] = float(space[key])
                elif self._dict_para_type[key] == 'string':
                    params[key] = space[key]

            self._options.append(option)
            self._name = name
            iter_result["param"] = params
            self._child_conn.send(iter_result)
            result = self._child_conn.recv()
            x_num = 0.0
            eval_list = result.split(',')
            for value in eval_list:
                num = float(value)
                x_num = x_num + num
            performance = x_num
            self._performance.append(performance)

        return self._options, self._performance

    def get_best_params(self):
        """return the parameters of the best performance"""
        params = {}
        best_index = np.argmin(self._performance)
        best_option = self._options[best_index]
        for i, val in enumerate(best_option):
            knob_val = val
            knob_name = self._name[i]
            if self._dict_para_type[knob_name] == 'int':
                params[knob_name] = int(knob_val)
            elif self._dict_para_type[knob_name] == 'float':
                params[knob_name] = float(knob_val)
            elif self._dict_para_type[knob_name] == 'string':
                params[knob_name] = knob_val
        LOGGER.info('best params: %s', params)
        return params, self._name

    def get_option_index(self, option):
        """return the index of the option list"""
        option_range_list = self._option_list
        option_index = []
        for i, val in enumerate(option):
            index = option_range_list[self._name[i]].items.index(val)
            option_index.append(index)
        return option_index

    def get_options_index(self, options):
        """return the options index of the options"""
        options_index = []
        for option in options:
            option_index = self.get_option_index(option)
            options_index.append(option_index)
        return options_index
