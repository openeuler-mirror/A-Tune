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
# Create: 2019-10-29

"""
This class is used to train models and characterize system workload.
"""

import os
import glob
from collections import Counter
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import train_test_split as tts
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.utils import class_weight
from xgboost import XGBClassifier


class WorkloadCharacterization:
    """train models and characterize system workload"""

    def __init__(self, model_path):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.tencoder = LabelEncoder()
        self.aencoder = LabelEncoder()
        self.dataset = None

    def parsing(self, data_path, header=0, analysis=False):
        """
        parse the data from csv
        :param data_path:  the path of csv
        :returns dataset:  converted data
        """
        df_content = []
        csvfiles = glob.glob(data_path)
        for csv in csvfiles:
            data = pd.read_csv(csv, index_col=None, header=header)
            df_content.append(data)
            dataset = pd.concat(df_content, sort=False)
        self.dataset = dataset
        if analysis:
            status_content = []
            for app, group in self.dataset.groupby('workload.appname'):
                status = group.describe()
                status['index'] = app
                status_content.append(status)
                total_status = pd.concat(status_content, sort=False)
            total_status.to_csv('datastatics.csv')
        return dataset

    def feature_selection(self, x_axis, y_axis, clfpath=None):
        """
        feature selection for classifiers
        :param x_axis, y_axis:  orginal input and output data
        :returns selected_x:  selected input data
        """
        x_scaled = StandardScaler().fit_transform(x_axis)
        x_train, x_test, y_train, y_test = tts(x_scaled, y_axis, test_size=0.3)
        model = RandomForestClassifier(n_estimators=500, random_state=0)
        weights = list(class_weight.compute_class_weight('balanced', np.unique(y_train), y_train))
        class_weights = dict(zip(np.unique(y_train), weights))
        w_array = np.ones(y_train.shape[0], dtype='float')
        for i, val in enumerate(y_train):
            w_array[i] = class_weights[val]
        model.fit(x_train, y_train, sample_weight=w_array)
        y_pred = model.predict(x_test)
        accuracy = accuracy_score(y_test, y_pred)
        print("the accuracy of current model is %f" % accuracy)
        importances = model.feature_importances_.tolist()
        features = self.dataset.iloc[:, :-2].columns.tolist()
        featureimportance = sorted(zip(features, importances), key=lambda x: -np.abs(x[1]))

        thresholds = sorted(set(importances), reverse=True)
        for thresh in thresholds:
            smodel = SelectFromModel(model, threshold=thresh, prefit=True)
            x_selected = smodel.transform(x_train)
            xt_selected = smodel.transform(x_test)

            feature_model = RandomForestClassifier(n_estimators=500, random_state=0)
            feature_model.fit(x_selected, y_train, sample_weight=w_array)
            y_pred = feature_model.predict(xt_selected)
            print("Current threshold value:%.2f, number of selected features: %d, "
                  "model accuracy:%.4f"
                  % (thresh, x_selected.shape[1], accuracy_score(y_test, y_pred)))
            if accuracy_score(y_test, y_pred) >= accuracy:
                feature_result = featureimportance[0:x_selected.shape[1]]
                print("The result of feature selection is:", feature_result)
                label = [result[0] for result in feature_result]
                selected_x = pd.DataFrame(x_axis, columns=label)
                if clfpath is not None:
                    joblib.dump(smodel, clfpath)
                return selected_x
        return x_axis

    @staticmethod
    def svm_clf(x_axis, y_axis, clfpath=None, kernel='rbf'):
        """
        svm_clf: support vector machine classifier
        """
        x_train, x_test, y_train, y_test = tts(x_axis, y_axis, test_size=0.5)

        rbf = svm.SVC(kernel=kernel, C=100, class_weight='balanced', gamma='auto')
        rbf.fit(x_train, y_train)
        rbf_score = rbf.score(x_test, y_test)
        print("the accuracy of svc is %f" % rbf_score)
        if clfpath is not None:
            joblib.dump(rbf, clfpath)
        return rbf

    @staticmethod
    def rf_clf(x_axis, y_axis, clfpath=None):
        """
        ada_clf: Adaptive Boosting classifier
        """
        x_train, x_test, y_train, y_test = tts(x_axis, y_axis, test_size=0.3)
        weights = list(class_weight.compute_class_weight('balanced', np.unique(y_train), y_train))
        class_weights = dict(zip(np.unique(y_train), weights))
        w_array = np.ones(y_train.shape[0], dtype='float')
        for i, val in enumerate(y_train):
            w_array[i] = class_weights[val]
        model = RandomForestClassifier(n_estimators=200, oob_score=True, random_state=0)
        model.fit(x_train, y_train, sample_weight=w_array)
        y_pred = model.predict(x_test)
        print("the accuracy of random forest classifier is %f" % accuracy_score(y_test, y_pred))
        if clfpath is not None:
            joblib.dump(model, clfpath)
        return model

    @staticmethod
    def xgb_clf(x_axis, y_axis, clfpath=None):
        """
        XGb_clf: XGBoost classifier
        """
        x_train, x_test, y_train, y_test = tts(x_axis, y_axis, test_size=0.3)
        weights = list(class_weight.compute_class_weight('balanced', np.unique(y_train), y_train))
        class_weights = dict(zip(np.unique(y_train), weights))
        w_array = np.ones(y_train.shape[0], dtype='float')
        for i, val in enumerate(y_train):
            w_array[i] = class_weights[val]
        model = XGBClassifier(learning_rate=0.1, n_estimators=400, max_depth=6,
                              min_child_weight=0.5, gamma=0.01, subsample=1, colsample_btree=1,
                              scale_pos_weight=1, random_state=27, slient=0, alpha=100)
        model.fit(x_train, y_train, sample_weight=w_array)
        y_pred = model.predict(x_test)
        print("the accuracy of xgboost classifier is %f" % accuracy_score(y_test, y_pred))
        if clfpath is not None:
            joblib.dump(model, clfpath)
        return model

    def train(self, data_path, feature_selection=False):
        """
        train the data from csv
        :param data:  the data path
        """
        tencoder_path = os.path.join(self.model_path, "tencoder.pkl")
        aencoder_path = os.path.join(self.model_path, "aencoder.pkl")
        scaler_path = os.path.join(self.model_path, "scaler.pkl")
        data_path = os.path.join(data_path, "*.csv")

        type_clf = os.path.join(self.model_path, "total_clf.m")
        type_feature = os.path.join(self.model_path, "total_feature.m")

        self.parsing(data_path)

        x_type = self.dataset.iloc[:, :-2]
        self.scaler.fit(x_type)
        y_type = self.tencoder.fit_transform(self.dataset.iloc[:, -2])
        y_app = self.aencoder.fit_transform(self.dataset.iloc[:, -1])
        joblib.dump(self.tencoder, tencoder_path)
        joblib.dump(self.aencoder, aencoder_path)
        joblib.dump(self.scaler, scaler_path)

        if feature_selection:
            selected_x = StandardScaler().fit_transform(
                self.feature_selection(x_type, y_type, type_feature))
        else:
            selected_x = StandardScaler().fit_transform(x_type)
        self.rf_clf(selected_x, y_type, clfpath=type_clf)
        print("The overall classifier has been generated.")

        for workload, group in self.dataset.groupby('workload.type'):
            x_app = group.iloc[:, :-2]
            y_app = self.aencoder.transform(group.iloc[:, -1])

            clf_name = workload + "_clf.m"
            feature_name = workload + "_feature.m"
            clf_path = os.path.join(self.model_path, clf_name)
            feature_path = os.path.join(self.model_path, feature_name)

            if feature_selection:
                selected_x = StandardScaler().fit_transform(
                    self.feature_selection(x_app, y_app, feature_path))
            else:
                selected_x = StandardScaler().fit_transform(x_app)
            self.rf_clf(selected_x, y_app, clf_path)
            print("The application classifiers have been generated.")

    def identify(self, data, feature_selection=False):
        """
        identify the workload_type according to input data
        :param data:  input data
        """
        data = pd.DataFrame(data)
        tencoder_path = os.path.join(self.model_path, "tencoder.pkl")
        aencoder_path = os.path.join(self.model_path, "aencoder.pkl")
        scaler_path = os.path.join(self.model_path, "scaler.pkl")

        type_path = os.path.join(self.model_path, "total_clf.m")
        df_path = os.path.join(self.model_path, "default_clf.m")
        tp_path = os.path.join(self.model_path, "throughput_performance_clf.m")

        self.scaler = joblib.load(scaler_path)
        self.tencoder = joblib.load(tencoder_path)
        self.aencoder = joblib.load(aencoder_path)

        type_clf = joblib.load(type_path)
        df_clf = joblib.load(df_path)
        tp_clf = joblib.load(tp_path)

        if feature_selection:
            feature_path = os.path.join(self.model_path, "total_feature.m")
            df_feature = os.path.join(self.model_path, "default_feature.m")
            tp_feature = os.path.join(self.model_path, "throughput_performance_feature.m")

            type_feat = joblib.load(feature_path)
            df_feat = joblib.load(df_feature)
            tp_feat = joblib.load(tp_feature)

        data = self.scaler.transform(data)
        if feature_selection:
            df_data = df_feat.transform(data)
            tp_data = tp_feat.transform(data)
            data = type_feat.transform(data)
        workload = type_clf.predict(data)
        workload = self.tencoder.inverse_transform(workload)
        print("Current workload:", workload)
        prediction = Counter(workload).most_common(1)[0]
        confidence = prediction[1] / len(workload)
        if confidence < 0.5:
            resourcelimit = 'default'
            return resourcelimit, "default", confidence
        if prediction[0] == 'throughput_performance':
            resourcelimit = "throughput"
            if feature_selection:
                data = tp_data
            result = tp_clf.predict(data)
        else:
            resourcelimit = "default"
            if feature_selection:
                data = df_data
            result = df_clf.predict(data)

        result = self.aencoder.inverse_transform(result)
        print(result)
        prediction = Counter(result).most_common(1)[0]
        confidence = prediction[1] / len(result)
        if confidence > 0.5:
            return resourcelimit, prediction[0], confidence
        return resourcelimit, "default", confidence

    def retrain(self, data_path, custom_path):
        """
        for user: train model according to the collecting data
        """
        custom_path = os.path.abspath(custom_path)
        (dirname, filename) = os.path.split(custom_path)
        (modelname, _) = os.path.splitext(filename)
        scalername = modelname + '_scaler.pkl'
        encodername = modelname + '_encoder.pkl'

        data_path = os.path.join(data_path, "*.csv")
        self.parsing(data_path, header=None)
        x_axis = self.scaler.fit_transform(self.dataset.iloc[:, :-1])
        y_axis = self.aencoder.fit_transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, os.path.join(dirname, scalername))
        joblib.dump(self.aencoder, os.path.join(dirname, encodername))

        class_num = len(self.aencoder.classes_)
        if class_num == 1:
            y_axis[-1] = y_axis[-1] + 1
        self.svm_clf(x_axis, y_axis, custom_path)

    @staticmethod
    def reidentify(data, custom_path):
        """
        for user: predict workload type
        """
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
        print(result)

        prediction = Counter(result).most_common(1)[0]
        confidence = prediction[1] / len(result)
        if confidence > 0.5:
            return prediction[0], confidence
        return "default", confidence
