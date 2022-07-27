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
# Create: 2020-08-02

"""
This class is used to perform weighted ensemble feature selection
to get really importance tuning parameters
"""

import logging
import multiprocessing
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import BaggingRegressor, AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import Ridge
from sklearn.tree import ExtraTreeRegressor


LOGGER = logging.getLogger(__name__)

class FeatureSelectorProcess(multiprocessing.Process):
    """class feature selector each with multiprocessing"""

    def __init__(self, regressor, list_sample_x, list_sample_y,
                 labels, index, sorted_index_queue, prediction_queue):
        multiprocessing.Process.__init__(self)
        self._regressor = regressor
        self._list_sample_x = list_sample_x
        self._list_sample_y = list_sample_y
        self._labels = labels
        self._index = index
        self._sorted_index = []
        self._sorted_index_queue = sorted_index_queue
        self._prediction_queue = prediction_queue

    @staticmethod
    def get_unified_feature_importance(regressor):
        """get unified feature importance for different type regressor"""
        if hasattr(regressor, "feature_importances_"):
            return regressor.feature_importances_
        elif hasattr(regressor, "coef_"):
            if hasattr(regressor, "support_vectors_"): # for SVR, return coef_[0]
                return regressor.coef_[0]
            return regressor.coef_
        elif hasattr(regressor, "estimators_features_"):
            feature_importances = np.mean([tree.feature_importances_ \
                    for tree in regressor.estimators_], axis=0)
            return feature_importances
        return None

    def get_ensemble_train_data(self):
        """get ensemble train data"""
        regressor = self._regressor
        prediction = regressor.predict(self._list_sample_x)
        return prediction

    def run(self):
        """main method to train the model and get ranked feature importance"""
        self._regressor.fit(self._list_sample_x, self._list_sample_y)
        unified_feature_importance = self.get_unified_feature_importance(self._regressor)
        result = zip(unified_feature_importance, self._labels, self._index)
        result = sorted(result, key=lambda x: -x[0])
        self._sorted_index = [i for coef, label, i in result]
        self._sorted_index_queue.put(self._sorted_index)
        prediction = self.get_ensemble_train_data()
        self._prediction_queue.put(prediction)


class WeightedEnsembleFeatureSelector:
    """class weighted ensemble feature selector"""

    def __init__(self):
        dtree = DecisionTreeRegressor()
        ranfor = RandomForestRegressor(n_estimators=10000, random_state=0, n_jobs=-1)
        graboo = GradientBoostingRegressor(n_estimators=10000, learning_rate=0.1)
        adb = AdaBoostRegressor(DecisionTreeRegressor(max_depth=16),
                                n_estimators=10000, random_state=0)
        bag = BaggingRegressor(base_estimator=ExtraTreeRegressor(max_depth=16),
                               n_estimators=10000, random_state=0, n_jobs=-1)
        self._regressors = [dtree, ranfor, graboo, adb, bag]
        self._ensemble_model = Ridge(alpha=10, max_iter=1000000)
        LOGGER.info('Weighted Ensemble Feature Selector using: '
                    'DecisionTree, RandomForest, GradientBoosting, AdaBoost, Bagging')

    def get_native_feature_importances_parallel(self, list_sample_x, list_sample_y, labels, index):
        """get native feature importances in parallel with multiple threading"""
        native_feature_importances = []
        fs_thread_list = []
        sorted_index_queue_list = []
        prediction_queue_list = []

        for regressor in self._regressors:
            sorted_index_queue = multiprocessing.Queue()
            prediction_queue = multiprocessing.Queue()
            fs_thread = FeatureSelectorProcess(regressor, list_sample_x, list_sample_y,
                                               labels, index, sorted_index_queue, prediction_queue)
            fs_thread_list.append(fs_thread)
            sorted_index_queue_list.append(sorted_index_queue)
            prediction_queue_list.append(prediction_queue)
            fs_thread.start()
        for fs_thread in fs_thread_list:
            fs_thread.join()

        for sorted_index_queue in sorted_index_queue_list:
            native_fi = sorted_index_queue.get()
            native_feature_importances.append(native_fi)
        LOGGER.info('get sorted index queue list')

        predictions = []
        for prediction_queue in prediction_queue_list:
            prediction = prediction_queue.get()
            predictions.append(prediction)
        LOGGER.info('get prediction queue list')

        return native_feature_importances, predictions

    @staticmethod
    def get_ensemble_train_datas(list_sample_x, predictions):
        """get ensemble train datas"""
        train_datas = []
        for i in range(len(list_sample_x)):
            train_data = []
            for _, val in enumerate(predictions):
                train_data.append(val[i])
            train_datas.append(train_data)
        return train_datas

    def get_ensemble_weights(self, list_sample_x, list_sample_y, predictions):
        """get ensemble weights"""
        ensemble_train_datas = self.get_ensemble_train_datas(list_sample_x, predictions)
        self._ensemble_model.fit(ensemble_train_datas, list_sample_y)
        orig_weight = self._ensemble_model.coef_
        orig_weight -= np.max(orig_weight)
        softmax_weight = np.exp(orig_weight) / np.sum(np.exp(orig_weight))
        return softmax_weight

    def get_ensemble_feature_importance(self, list_sample_x, list_sample_y, labels):
        """Make sure the input list_sample_x is preprocessed with StandardScaler"""
        index = list(range(len(labels)))
        native_feature_importances, predictions = self.get_native_feature_importances_parallel(
            list_sample_x, list_sample_y, labels, index)
        LOGGER.info('Get feature importances for each model: %s', native_feature_importances)
        ensemble_weights = self.get_ensemble_weights(list_sample_x, list_sample_y, predictions)
        LOGGER.info('Get ensemble weights for each model: %s', ensemble_weights)

        ensemble_scores = [0 for i in range(len(list_sample_x[0]))]
        for j, val in enumerate(ensemble_weights):
            en_weight = val
            native_fi = native_feature_importances[j]
            feature_num = len(native_fi)
            for i, value in enumerate(native_fi):
                feature_index = value
                ensemble_scores[feature_index] += \
                    en_weight * (feature_num - i)  # the larger, the better
        ensemble_result = zip(ensemble_scores, labels, index)
        ensemble_result = sorted(ensemble_result, key=lambda x: -x[0])
        rank = ", ".join(f"{label}: {round(score, 3)}"
                         for score, label, i in ensemble_result)

        sorted_index = [i for score, label, i in ensemble_result]

        LOGGER.info('ensemble rank: %s', rank)
        LOGGER.info('ensemble sorted_index: %s', sorted_index)

        return rank
