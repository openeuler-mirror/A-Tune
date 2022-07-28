#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) The Lab of Professor Weiwei Lin (linww@scut.edu.cn),
# School of Computer Science and Engineering, South China University of Technology.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2021-01-04

import logging
import copy
from functools import cmp_to_key

LOGGER = logging.getLogger(__name__)


class KnobTraverseManager:
    """Knob traverse manager"""

    def __init__(self, knobs, child_conn, default_values):
        self._knobs = knobs
        self._child_conn = child_conn
        self._default_values = self.default_values_to_dict(default_values)
        self._param_performance_map = {}
        self._name_list = []
        self._performIndex_knobsIndex = []
        self._max_eval = 0
        for p_nob in knobs:
            self._name_list.append(p_nob['name'])

    def get_default_values(self):
        """get the default values"""
        return self._default_values

    def default_values_to_dict(self, default_values):
        """change list format to dictionary format """
        default_value_dict = {}
        knobs = self._knobs
        for i in range(len(knobs)):
            name = knobs[i]['name']
            val = default_values[i]
            if len(val) == 0:
                default_value_dict[name] = ''
            else:
                default_value_dict[name] = self.get_value_with_type(i, val)
        return default_value_dict

    def get_value_with_type(self, i, val):
        """change the type to the original type"""
        if self._knobs[i]['dtype'] == 'int':
            return int(val)
        if self._knobs[i]['dtype'] == 'float':
            return float(val)
        if self._knobs[i]['dtype'] == 'string':
            return val
        return val

    def get_traverse_list(self):
        """get the list of parameters for the tra algorithm,
            return a two-dimensional list """
        knobs = self._knobs
        default_values = self._default_values
        traverse_list = []  # format like [[1,2,3],[2,3,1],...]

        # add the default parameters into traverse_list to get the baseline performance
        default_param_val_list = [str(default_values[knobs[i]['name']]) for i in range(len(knobs))]
        self._performIndex_knobsIndex.append(-1)
        traverse_list.append(default_param_val_list)

        for i in range(len(knobs)):
            test_param_val_list = []
            if knobs[i]['options'] is not None:
                for param_val in knobs[i]['options']:
                    if str(param_val) != str(default_values[knobs[i]['name']]):
                        test_param_val_list.append(str(param_val))
            else:
                r_range = knobs[i]['range']
                length = len(r_range) if len(r_range) % 2 == 0 else len(r_range) - 1
                range_list = r_range[:length]
                min_val, max_val = min(range_list), max(range_list)
                if str(max_val) != str(default_values[knobs[i]['name']]):
                    test_param_val_list.append(max_val)
                if str(min_val) != str(default_values[knobs[i]['name']]):
                    test_param_val_list.append(min_val)

            for j in range(len(test_param_val_list)):
                tmp_item = copy.deepcopy(default_param_val_list)
                tmp_item[i] = str(test_param_val_list[j])
                self._performIndex_knobsIndex.append(i)
                traverse_list.append(tmp_item)

        self._max_eval = len(traverse_list)
        self._child_conn.send(self._max_eval)
        LOGGER.debug("traverse list is %s", traverse_list)
        return traverse_list

    def get_traverse_performance(self, knobs_list):
        """get the performance for each parameters list in knobs_list"""
        performance_results = []
        for knob in knobs_list:
            result = self.do_one_knob_test(knob)
            performance_results.append(result)
        LOGGER.debug("traverse performance is %s", performance_results)
        return performance_results

    def do_one_knob_test(self, set_knob_val_vec):
        iter_result = {}
        params = {}

        for i, val in enumerate(set_knob_val_vec):
            knob_val = val
            knob_name = self._name_list[i]
            if len(val) == 0:
                continue
            params[knob_name] = self.get_value_with_type(i, knob_val)

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

    def rank_list_compare(self, s1, s2):
        """rank compare operator function"""
        if s1[1] < s2[1]:
            return -1
        elif s1[1] > s2[1]:
            return 1
        else:
            if self._param_performance_map[s1[0]] < self._param_performance_map[s2[0]]:
                return -1
            else:
                return 1

    def get_traverse_rank(self, performance):
        """get the rank of parameters according to the performance"""
        knobs = self._knobs
        param_performance_map = self._param_performance_map
        param_differ_perform_map = {}

        index = 1
        while index < len(self._performIndex_knobsIndex):
            param_name = knobs[self._performIndex_knobsIndex[index]]['name']

            # process for parameters of options type
            if knobs[self._performIndex_knobsIndex[index]]['options'] is not None:
                end_index = index + 1
                while (end_index < len(self._performIndex_knobsIndex) and
                       knobs[self._performIndex_knobsIndex[end_index]]['name'] == param_name):
                    end_index += 1
                options_list = performance[index:end_index]
                options_list.append(performance[0])
                options_min, options_max = min(options_list), max(options_list)
                param_performance_map[param_name] = options_min
                param_differ_perform_map[param_name] = abs(options_max - options_min)
                index = end_index
                continue

            # process for parameters of range type
            if knobs[self._performIndex_knobsIndex[index]]['range'] is not None:
                param_performance_map[param_name] = performance[index]
                next_item_param_name = 'None'
                if (index + 1) < len(self._performIndex_knobsIndex):  # avoid out of range
                    next_item_param_name = knobs[self._performIndex_knobsIndex[index + 1]]['name']
                # If the default value is already the maximum or minimum value, the parameter has
                # only one performance, which is directly subtracted from the default value,
                # otherwise, the maximum value (performance) is subtracted from the minimum value
                # (performance)
                if next_item_param_name != param_name:
                    param_differ_perform_map[param_name] = abs(performance[index] - performance[0])
                else:
                    param_differ_perform_map[param_name] = abs(performance[index] -
                                                               performance[index + 1])
                    param_performance_map[param_name] = min(param_performance_map[param_name],
                                                            performance[index + 1])
                    index += 1

            index += 1

        # sort the param_performance_map in ascending order
        sorted_param_performance_pair = sorted(
            param_performance_map.items(), key=lambda kv: (kv[1], kv[0]), reverse=False)
        # sort the param_differ_perform_map in descending order
        sorted_param_differ_perform_pair = sorted(
            param_differ_perform_map.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

        rank_map = {}
        for i in range(len(sorted_param_performance_pair)):
            if sorted_param_performance_pair[i][0] in rank_map.keys():
                rank_map[sorted_param_performance_pair[i][0]] += (i + 1)
            else:
                rank_map[sorted_param_performance_pair[i][0]] = (i + 1)
            if sorted_param_differ_perform_pair[i][0] in rank_map.keys():
                rank_map[sorted_param_differ_perform_pair[i][0]] += (i + 1)
            else:
                rank_map[sorted_param_differ_perform_pair[i][0]] = (i + 1)

        # sort the rank_list by ascending, if rank is same and sort by performance
        rank_list = list(zip(list(rank_map), list(rank_map.values())))
        rank_list = sorted(rank_list, key=cmp_to_key(self.rank_list_compare))
        length = len(rank_list)
        rank = ", ".join(f"{rank_list[i][0]}: {str(length - i)}" for i in range(length))
        LOGGER.debug("traverse rank is %s", rank)
        return rank
