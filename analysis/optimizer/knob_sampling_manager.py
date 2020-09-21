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
This class is used to perform lhs(Latin hypercube sampling),
to get 'balanced' sampling configuration and its performance
"""

import logging
import numpy as np
import lhsmdu

LOGGER = logging.getLogger(__name__)


class KnobSampling:
    """knob sampling"""

    def __init__(self, p_nob, split_count=5):
        option_range = []
        if p_nob['dtype'] == 'string':
            option_range.extend(p_nob['options'])
        elif p_nob['dtype'] == 'int' or p_nob['dtype'] == 'float':
            items = p_nob['items']
            if items is not None:
                for item in items:
                    option_range.append(str(item))
            step = 1
            if p_nob['range'] is not None:
                if 'step' in p_nob.keys():
                    if p_nob['dtype'] == 'int':
                        step = int((p_nob['range'][1] - p_nob['range'][0]) / (split_count - 1))
                    elif p_nob['dtype'] == 'float':
                        step = float((p_nob['range'][1] - p_nob['range'][0]) / (split_count - 1))
                item_val = p_nob['range'][0]
                for _ in range(split_count):
                    option_range.append(str(item_val))
                    item_val += step

        self.option_range = option_range


class KnobSamplingManager:
    """knob sample manager"""

    def __init__(self, knobs, child_conn, sample_count, split_count, algorithm='lhs'):
        option_range_list = []
        name_list = []
        for p_nob in knobs:
            knob_sampling = KnobSampling(p_nob, split_count)
            option_range_list.append(knob_sampling.option_range)
            name_list.append(p_nob['name'])
        self._option_range_list = option_range_list
        self._knobs = knobs
        self._name_list = name_list
        self._child_conn = child_conn
        self._sample_count = sample_count
        self._algorithm = algorithm
        self._is_discrete = []
        self._value_count = []
        self._value_min = []

        for i in range(len(self._option_range_list)):
            option_range = self._option_range_list[i]
            if isinstance(option_range, list):
                self._is_discrete.append(True)
                self._value_count.append(float(len(option_range)))
                self._value_min.append(float(0))
            elif isinstance(option_range, tuple):
                self._is_discrete.append(False)
                self._value_count.append(float(option_range[1] - option_range[0]))
                self._value_min = float(option_range[0])

    def get_rate_samples(self):
        """
        Note: return type is matrix, access with rates[i, j] NOT rates[i][j]
        """
        if self._algorithm == 'lhs':
            rates = lhsmdu.sample(len(self._option_range_list), self._sample_count)
            return rates
        if self._algorithm == 'mcs':
            rates = lhsmdu.createRandomStandardUniformMatrix(
                len(self._option_range_list), self._sample_count)
            return rates
        rates = lhsmdu.sample(len(self._option_range_list), self._sample_count)
        return rates

    def get_sample_from_rate(self, dim, rate):
        """return the sample depend on rate"""
        if self._is_discrete[dim]:
            index = int(self._value_count[dim] * rate)
            return self._option_range_list[dim][index]
        return self._value_min[dim] + self._value_count[dim] * rate

    def get_knob_samples(self):
        """get knob samples"""
        rates = self.get_rate_samples()
        LOGGER.info('Get lhs rates:%s', rates)
        knob_samples = []
        for i in range(self._sample_count):
            knob_sample = []
            for dim in range(len(self._option_range_list)):
                rate = rates[dim, i]
                sample = self.get_sample_from_rate(dim, rate)
                knob_sample.append(sample)
            knob_samples.append(knob_sample)
        LOGGER.info('Get lhs samples: %s', knob_samples)
        return knob_samples

    def get_knob_samples_horizontal(self):
        """get knob samples in horizontal"""
        rates = self.get_rate_samples()
        LOGGER.info(rates)
        knob_samples = []
        for dim in range(len(self._option_range_list)):
            knob_sample = []
            for i in range(self._sample_count):
                rate = rates[dim, i]
                sample = self.get_sample_from_rate(dim, rate)
                knob_sample.append(sample)
            knob_samples.append(knob_sample)
        return knob_samples

    @staticmethod
    def construct_one_knob_sample(knob_samples, index):
        """construct one knob sample"""
        return knob_samples[index]

    def test_performance_one_knob_sample(self, knob_samples, index):
        """test performance of one knob sample"""
        set_knob_val_vec = self.construct_one_knob_sample(knob_samples, index)
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
        LOGGER.info('knob sample: %s, result: %s', set_knob_val_vec, performance)
        return performance

    def do_knob_sampling_test(self, knob_samples):
        """test knob sampling"""
        results = []
        for index in range(self._sample_count):
            result = self.test_performance_one_knob_sample(knob_samples, index)
            results.append(result)
        return results

    def get_best_params(self, knob_samples, results):
        """get best_params"""
        np_results = np.array(results)
        best_index = np.argmin(np_results)
        set_knob_val_vec = self.construct_one_knob_sample(knob_samples, best_index)
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
        return params

    def get_option_index(self, option):
        """return the index of the option"""
        option_range_list = self._option_range_list
        option_index = []
        for i, val in enumerate(option):
            index = option_range_list[i].index(val)
            option_index.append(index)
        return option_index

    def get_options_index(self, options):
        """return the options's index"""
        options_index = []
        for option in options:
            option_index = self.get_option_index(option)
            options_index.append(option_index)
        return options_index
