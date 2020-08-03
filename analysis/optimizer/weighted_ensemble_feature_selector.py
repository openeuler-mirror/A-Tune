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

import numpy as np
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import BaggingRegressor, AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import ElasticNet, Ridge

import logging

LOGGER = logging.getLogger(__name__)


class WeightedEnsembleFeatureSelector(object):
    """class weighted ensemble feature selector"""
    def __init__(self):
        lasso = Lasso(alpha=0.0005, max_iter=1000000)
        rf = RandomForestRegressor(n_estimators=10000, random_state=0, n_jobs=-1)
        gb = GradientBoostingRegressor(n_estimators=10000, learning_rate=0.1)
        en = ElasticNet(alpha=0.0003, max_iter=1000000, l1_ratio=0.8)
        adb = AdaBoostRegressor(DecisionTreeRegressor(max_depth=16),\
                n_estimators=10000, random_state=0)
        bag = BaggingRegressor(base_estimator=DecisionTreeRegressor(max_depth=16),\
                n_estimators=10000)
        self._regressors = [lasso, rf, gb, en, adb, bag]
        self._ensemble_model = Ridge(alpha=10, max_iter=1000000)
        LOGGER.info('Weighted Ensemble Feature Selector using: \
                Lasso, RandomForest, GradientBoosting, ElasticNet, AdaBoost, Bagging')

    def get_unified_feature_importance(self, regressor):
        """get unified feature importance"""
        if hasattr(regressor, "feature_importances_"):
            return regressor.feature_importances_
        elif hasattr(regressor, "coef_"):
            return np.abs(regressor.coef_)
        elif hasattr(regressor, "estimators_features_"):
            feature_importances = np.mean([tree.feature_importances_ \
                    for tree in regressor.estimators_], axis=0)
            return feature_importances
        return None

    def get_one_native_feature_importance(self, regressor, \
            list_sample_x, list_sample_y, labels, index):
        """get one native feature importance, just fit data once"""
        regressor.fit(list_sample_x, list_sample_y)
        unified_feature_importance = self.get_unified_feature_importance(regressor)
        result = zip(unified_feature_importance, labels, index)
        result = sorted(result, key=lambda x: -x[0])
        sorted_index = [i for coef, label, i in result]
        return sorted_index

    def get_native_feature_importances(self, list_sample_x, list_sample_y, labels, index):
        """get natice feature importance"""
        native_feature_importances = []
        for regressor in self._regressors:
            native_fi = self.get_one_native_feature_importance(regressor, \
                    list_sample_x, list_sample_y, labels, index)
            native_feature_importances.append(native_fi)
        return native_feature_importances

    def get_ensemble_train_datas(self, list_sample_x):
        """get ensemble train datas"""
        predictions = []
        for regressor in self._regressors:
            prediction = regressor.predict(list_sample_x)
            predictions.append(prediction)
        train_datas = []
        for i in range(len(list_sample_x)):
            train_data = []
            for j in range(len(predictions)):
                train_data.append(predictions[j][i])
            train_datas.append(train_data)
        return train_datas

    def get_ensemble_weights(self, list_sample_x, list_sample_y):
        """get ensemble weights"""
        ensemble_train_datas = self.get_ensemble_train_datas(list_sample_x)
        self._ensemble_model.fit(ensemble_train_datas, list_sample_y)
        orig_weight = self._ensemble_model.coef_
        orig_weight -= np.max(orig_weight)
        softmax_weight = np.exp(orig_weight) / np.sum(np.exp(orig_weight))
        return softmax_weight

    def get_ensemble_feature_importance(self, list_sample_x, list_sample_y, labels):
        """Make sure the input list_sample_x is preprocessed with StandardScaler"""
        index = [i for i in range(len(labels))]
        native_feature_importances = self.get_native_feature_importances( \
                list_sample_x, list_sample_y, labels, index)
        LOGGER.info('Get feature importances for each model: %s', native_feature_importances)
        ensemble_weights = self.get_ensemble_weights(list_sample_x, list_sample_y)
        LOGGER.info('Get ensemble weights for each model: %s', ensemble_weights)

        ensemble_scores = [0 for i in range(len(list_sample_x[0]))]
        for e in range(len(ensemble_weights)):
            en_weight = ensemble_weights[e]
            native_fi = native_feature_importances[e]
            feature_num = len(native_fi)
            for i in range(len(native_fi)):
                feature_index = native_fi[i]
                ensemble_scores[feature_index] += \
                        en_weight * (feature_num - i) # the larger, the better
        ensemble_result = zip(ensemble_scores, labels, index)
        ensemble_result = sorted(ensemble_result, key=lambda x: -x[0])
        rank = ", ".join("%s: %s" % (label, round(score, 3)) \
                for score, label, i in ensemble_result)

        sorted_index = [i for score, label, i in ensemble_result]

        LOGGER.info('ensemble rank: %s', rank)
        LOGGER.info('ensemble sorted_index: %s', sorted_index)

        return rank, sorted_index
