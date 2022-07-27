#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2020-10-09

"""
This class is used to perform variance reduction feature selection
to get really importance tuning parameters
"""

import logging
import numpy as np

LOGGER = logging.getLogger(__name__)


class VarianceReductionFeatureSelector:
    """class variance reduction feature selector"""

    @staticmethod
    def get_ensemble_feature_importance(list_sample_x, list_sample_y, labels):
        """Make sure the input list_sample_x is preprocessed with StandardScaler"""
        if len(list_sample_x) == 0:
            return None
        global_variance = np.std(list_sample_y)
        list_pi = []
        for i in range(len(list_sample_x[0])):
            dict_sample = {}
            for j, val in enumerate(list_sample_x):
                if val[i] not in dict_sample.keys():
                    dict_sample[val[i]] = [list_sample_y[j]]
                else:
                    dict_sample[val[i]].append(list_sample_y[j])
            variance_sum = 0
            for value in dict_sample.values():
                variance_sum += np.std(value)
            list_pi.append(global_variance - variance_sum)

        index = list(range(len(labels)))
        ensemble_result = zip(list_pi, labels, index)
        ensemble_result = sorted(ensemble_result, key=lambda x: -x[0])
        rank = ", ".join(f"{label}: {round(score, 3)}" for score, label, i in ensemble_result)
        sorted_index = [i for score, label, i in ensemble_result]
        LOGGER.info('ensemble rank: %s', rank)
        LOGGER.info('ensemble sorted_index: %s', sorted_index)
        return rank
