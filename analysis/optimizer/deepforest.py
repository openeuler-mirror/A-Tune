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
# Create: 2023-09-20

import numpy as np
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
import logging

LOGGER = logging.getLogger(__name__)

class CascadeForestClassifier:
    
    def __init__(self, n_estimators=10, max_layers=10, random_state=None):
        self.n_estimators = n_estimators
        self.max_layers = max_layers
        self.random_state = random_state
        self.layers = []

    def fit(self, X, y):
        layer = 0
        while layer < self.max_layers:
            LOGGER.info('space %s', layer + 1)
            layer_estimators = []
            for i in range(self.n_estimators):
                if i % 2 == 0:
                    estimator = RandomForestClassifier(n_jobs=-1, random_state=self.random_state)
                else:
                    estimator = ExtraTreesClassifier(n_jobs=-1, random_state=self.random_state)
                estimator.fit(X, y)
                layer_estimators.append(estimator)
            self.layers.append(layer_estimators)
            X_new = self._generate_features(X)
            if np.array_equal(X, X_new):
                break
            X = X_new
            layer += 1

    def predict(self, X):
        X_new = X
        for layer_estimators in self.layers:
            X_new = self._generate_features(X_new, layer_estimators)
        return np.argmax(X_new, axis=1)

    def _generate_features(self, X, layer_estimators=None):
        if layer_estimators is None:
            layer_estimators = self.layers[-1]
        features = []
        for estimator in layer_estimators:
            probas = estimator.predict_proba(X)
            features.extend(np.transpose(probas))
        return np.column_stack(features)