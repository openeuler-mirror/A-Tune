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
# Create: 2023-08-22

"""
This class is used to train models and characterize system workload and application types.
"""

import os
import glob
import collections
import numpy as np
import pandas as pd
import joblib
import subprocess
import re
from sklearn.linear_model import Lasso
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import recall_score
from sklearn.model_selection import train_test_split as tts
from sklearn.metrics import accuracy_score
from analysis.optimizer.workload_characterization import WorkloadCharacterization
from analysis.optimizer.bottleneck_characterization import BottleneckCharacterization
from analysis.optimizer.deepforest import CascadeForestClassifier
import logging

LOGGER = logging.getLogger(__name__)

class AppCharacterization(WorkloadCharacterization):
    """train models and characterize application"""

    def __init__(self, model_path, mode="all"):
        super().__init__(model_path)

        self.perf_indicator = ['PERF.STAT.IPC', 'PERF.STAT.CACHE-MISS-RATIO', 'PERF.STAT.MPKI',
                        'PERF.STAT.ITLB-LOAD-MISS-RATIO', 'PERF.STAT.DTLB-LOAD-MISS-RATIO',
                        'PERF.STAT.SBPI', 'PERF.STAT.SBPC', ]
        
        self.consider_perf = self.consider_perf_detection()
        
        if mode == "all":
            self.bottleneck = BottleneckCharacterization()
    
    def consider_perf_detection(self):
        output = subprocess.check_output("perf stat -a -e cycles --interval-print 1000 --interval-count 1".split(), stderr=subprocess.STDOUT)
        event = 'cycles'
        pattern = r"^\ {2,}(\d.*?)\ {2,}(\d.*?)\ {2,}(\w*)\ {2,}(" + event + r")\ {1,}.*"
        search_obj = re.search(pattern, output.decode(), re.UNICODE | re.MULTILINE)
        if search_obj == None:
            return False
        return True

    def parsing(self, data_path, data_features, header=0, analysis=False):
        """
        parse the data from csv
        :param data_path:  the path of csv
        """
        df_content = []
        csvfiles = glob.glob(data_path)
        selected_cols = list(data_features)
        selected_cols.append('workload.type')
        selected_cols.append('workload.appname')

        for csv in csvfiles:
            data = pd.read_csv(csv, index_col=None, header=header, usecols=selected_cols)
            data[data_features] = self.abnormal_detection(data[data_features])
            df_content.append(data.dropna(axis=0))
        self.dataset = pd.concat(df_content, sort=False)
        if analysis:
            status_content = []
            for app, group in self.dataset.groupby('workload.appname'):
                status = group.describe()
                status['index'] = app
                status_content.append(status)
                total_status = pd.concat(status_content, sort=False)
            total_status.to_csv('statistics.csv')

    def feature_selection(self, x_axis, y_axis, data_features, clfpath=None):
        """
        feature selection for classifiers
        :param x_axis, y_axis:  orginal input and output data
        :returns selected_x:  selected input data
        """
        lasso = Lasso(alpha=0.01).fit(x_axis, y_axis)
        importance = lasso.coef_.tolist()
        featureimportance = sorted(zip(data_features, importance), key=lambda x: -np.abs(x[1]))
        result = ", ".join(f"{label}: {round(coef, 3)}" for label, coef in featureimportance)
        LOGGER.info('Feature selection result of current classifier: %s', result)
        
        # Store selected column names into a list and return it as output 
        self.selected_columns = [feat[0] for feat in featureimportance if abs(feat[1]) > 0.001]
        LOGGER.info('selected_columns: %s', self.selected_columns)
        
        feature_model = SelectFromModel(lasso, threshold=0.001)
        selected_x = feature_model.fit_transform(x_axis, y_axis)
        if clfpath is not None:
            joblib.dump(feature_model, clfpath)
        return selected_x
    
    @staticmethod
    def drf_clf(x_axis, y_axis, clfpath=None):
        """
        drf_clf: deep-rf classifier
        """
        x_train, x_test, y_train, y_test = tts(x_axis, y_axis, test_size=0.3,)
        
        model = CascadeForestClassifier(n_estimators=6, max_layers=8, random_state=42)
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        LOGGER.info('the accuracy of svc classifier is: %s', accuracy_score(y_test, y_pred))
        LOGGER.info('the recall of deep-rf classifier is: %s', recall_score(y_test, y_pred, average='macro'))
        if clfpath is not None:
            joblib.dump(model, clfpath)
        return model
    
    def get_consider_perf(self, consider_perf):
        if not consider_perf:
            data_features = [item for item in self.data_features if item not in self.perf_indicator]
        else:
            data_features = self.data_features
        return data_features

    def train(self, data_path, feature_selection=False, search=False, model='drf', consider_perf=None):
        """
        train the data from csv
        :param data_path:  the data path
        :param object: type or app
        :param model: training model, currently supports rf, deep-rf, svm and xgboost
        :param feature_selection:  whether to perform feature extraction
        :param search: whether to perform hyperparameter search
        :param consider_perf: whether to consider perf indicators
        """
        if consider_perf == None:
            consider_perf = self.consider_perf
            
        data_features = self.get_consider_perf(consider_perf)   
        
        tencoder_path = os.path.join(self.model_path, "tencoder.pkl")
        aencoder_path = os.path.join(self.model_path, "aencoder.pkl")
        scaler_path = os.path.join(self.model_path, "scaler.pkl")
        data_path = os.path.join(data_path, "*.csv")

        type_model_clf = os.path.join(self.model_path, 'type_' + model + "_clf.m")
        app_model_clf = os.path.join(self.model_path, 'app_' + model + "_clf.m")
        type_feature = os.path.join(self.model_path, "type_feature.m")
        app_feature = os.path.join(self.model_path, "app_feature.m")

        self.parsing(data_path, data_features)

        x = self.dataset.iloc[:, :-2]
        self.scaler.fit_transform(x)
        
        type_y = self.tencoder.fit_transform(self.dataset.iloc[:, -2])
        app_y = self.aencoder.fit_transform(self.dataset.iloc[:, -1])
        
        joblib.dump(self.tencoder, tencoder_path)
        joblib.dump(self.aencoder, aencoder_path)
        joblib.dump(self.scaler, scaler_path)

        if feature_selection:
            type_x = self.feature_selection(x, type_y, data_features, type_feature)
            app_x = self.feature_selection(x, app_y, data_features, app_feature)
        else:
            type_x = app_x = x

        if model == 'rf':
            LOGGER.info('workload type model start training')
            self.rf_clf(type_x, type_y, clfpath=type_model_clf, search=search)
            LOGGER.info('app model start training')
            self.rf_clf(app_x, app_y, clfpath=app_model_clf, search=search)
        elif model == 'svm':
            LOGGER.info('workload type model start training')
            self.svm_clf(type_x, type_y, clfpath=type_model_clf, search=search)
            LOGGER.info('app model start training')
            self.svm_clf(app_x, app_y, clfpath=app_model_clf, search=search)
        elif model == 'xgb':
            LOGGER.info('workload type model start training')
            self.xgb_clf(type_x, type_y, clfpath=type_model_clf)
            LOGGER.info('app model start training')
            self.xgb_clf(app_x, app_y, clfpath=app_model_clf)
        elif model == 'drf':
            LOGGER.info('workload type model start training')
            self.drf_clf(type_x, type_y, clfpath=type_model_clf)
            LOGGER.info('app model start training')
            self.drf_clf(app_x, app_y, clfpath=app_model_clf)
        LOGGER.info('The overall classifier has been generated.')


    def identify(self, data, feature_selection=False, model='drf', consider_perf=None):
        """
        identify the workload_type according to input data
        :param data:  input data
        :param feature_selection:  whether to perform feature extraction
        :param consider_perf: whether to consider perf indicators
        """
        if consider_perf == None:
            consider_perf = self.consider_perf
            
        data_features = self.get_consider_perf(consider_perf)
        
        cpu_exist, mem_exist, net_quality_exist, net_io_exist, disk_io_exist = self.bottleneck.search_bottleneck(data)
        bottleneck_binary = (int(cpu_exist) << 4) | (int(mem_exist) << 3) | (int(net_quality_exist) << 2) | (int(net_io_exist) << 1) | int(disk_io_exist)

        data = data[data_features]

        tencoder_path = os.path.join(self.model_path, "tencoder.pkl")
        aencoder_path = os.path.join(self.model_path, "aencoder.pkl")
        scaler_path = os.path.join(self.model_path, "scaler.pkl")

        type_model_path = os.path.join(self.model_path, 'type_' + model + "_clf.m")
        app_model_path = os.path.join(self.model_path, 'app_' + model + "_clf.m")

        self.scaler = joblib.load(scaler_path)
        self.tencoder = joblib.load(tencoder_path)
        self.aencoder = joblib.load(aencoder_path)

        type_model_clf = joblib.load(type_model_path)
        app_model_clf = joblib.load(app_model_path)

        data = self.scaler.transform(data)

        if feature_selection:
            type_feature = os.path.join(self.model_path, "type_feature.m")
            app_feature = os.path.join(self.model_path, "app_feature.m")
    
            type_model_feat = joblib.load(type_feature)
            type_data = type_model_feat.transform(data)
            
            app_model_feat = joblib.load(app_feature)
            app_data = app_model_feat.transform(data)
        else:
            type_data = app_data = data
        
        type_result = type_model_clf.predict(type_data)
        type_result = self.tencoder.inverse_transform(type_result)
        
        app_result = app_model_clf.predict(app_data)
        app_result = self.aencoder.inverse_transform(app_result)
        
        type_prediction = collections.Counter(type_result).most_common(1)[0]
        app_prediction = collections.Counter(app_result).most_common(1)[0]
        
        type_confidence = type_prediction[1] / len(type_result)
        app_confidence = app_prediction[1] / len(app_result) 
        
        if type_confidence < 0.5:
            resourcelimit = 'default'
        else:
            resourcelimit = type_prediction[0]
        
        if app_confidence < 0.5:
            applimit = 'default'
        else:
            applimit = app_prediction[0]
            
        return bottleneck_binary, resourcelimit, applimit, app_confidence
    
    def reidentify(self, data, custom_path):
        """
        for user: predict workload type
        """
        cpu_exist, mem_exist, net_quality_exist, net_io_exist, disk_io_exist = self.bottleneck.search_bottleneck(data)
        bottleneck_binary = (int(cpu_exist) << 4) | (int(mem_exist) << 3) | (int(net_quality_exist) << 2) | (int(net_io_exist) << 1) | int(disk_io_exist)

        data = data[self.data_features]
        custom_path = os.path.abspath(custom_path)
        (dirname, filename) = os.path.split(custom_path)
        (modelname, _) = os.path.splitext(filename)
        scalername = modelname + '_scaler.pkl'
        encodername = modelname + '_encoder.pkl'

        scaler = joblib.load(os.path.join(dirname, scalername))
        encoder = joblib.load(os.path.join(dirname, encodername))
        model = joblib.load(custom_path)

        data = scaler.transform(data)
        result = model.predict(data)
        result = encoder.inverse_transform(result)

        prediction = collections.Counter(result).most_common(1)[0]
        confidence = prediction[1] / len(result)
        if confidence > 0.5:
            return bottleneck_binary, prediction[0], confidence
        return bottleneck_binary, "default", confidence