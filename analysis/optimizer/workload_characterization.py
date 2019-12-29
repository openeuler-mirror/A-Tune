#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v1.
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
# Create: 2019-10-29

"""
This class is used to train models and characterize system workload.
"""

import os
import glob
from collections import Counter
import pandas as pd
from xgboost import XGBClassifier
from sklearn import svm
from sklearn.cluster import KMeans
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split as tts
from sklearn.preprocessing import StandardScaler, LabelEncoder


class WorkloadCharacterization:
    """train models and characterize system workload"""

    def __init__(self, model_path):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.encoder = LabelEncoder()
        self.dataset = None
        self.x_axis = None
        self.y_axis = None

    def parsing(self, data_path):
        """
        parse the data from csv
        :param data_path:  the path of csv
        :returns dataset:  converted data
        """
        df_content = []
        csvfiles = glob.glob(data_path)
        for csv in csvfiles:
            data = pd.read_csv(csv, index_col=None, header=None)
            df_content.append(data)
            dataset = pd.concat(df_content)
        self.dataset = dataset
        return dataset

    def clustering(self, data_path):
        """
        clustering for the data from csv
        :param data_path:  the path of csv
        """
        complete_path = os.path.join(data_path, "*.csv")
        self.parsing(complete_path)
        dataset = self.dataset.drop([28, 41, 42, 43, 44, 57, 58], axis=1)
        cpu_util = pd.concat([dataset.iloc[:, 8], dataset.iloc[:, 45]], axis=1, join='inner')
        io_util = pd.concat([dataset.iloc[:, 3], dataset.iloc[:, 19]], axis=1, join='inner')
        net_util = dataset.iloc[:, 25]
        mem_total = dataset.iloc[:, 29]

        cpu = KMeans(n_clusters=2).fit(cpu_util)
        joblib.dump(cpu, os.path.join(self.model_path, 'cpu_clu.m'))
        dataset.insert(0, 'cpu', cpu.predict(cpu_util))

        io_data = KMeans(n_clusters=2).fit(io_util)
        joblib.dump(io_data, os.path.join(self.model_path, 'io_clu.m'))
        dataset.insert(1, 'io', io_data.predict(io_util))

        net_data = [[x] for x in net_util]
        net = KMeans(n_clusters=2).fit(net_data)
        joblib.dump(net, os.path.join(self.model_path, 'net_clu.m'))
        dataset.insert(2, 'net', net.predict(net_data))

        mem_data = [[x] for x in mem_total]
        mem = KMeans(n_clusters=2).fit(mem_data)
        joblib.dump(mem, os.path.join(self.model_path, 'mem_clu.m'))
        dataset.insert(3, 'mem', mem.predict(mem_data))

        dataset['cpu'] = dataset['cpu'].map(str)
        dataset['io'] = dataset['io'].map(str)
        dataset['net'] = dataset['net'].map(str)
        dataset['mem'] = dataset['mem'].map(str)
        result = dataset['cpu'].str.cat(dataset['io'])
        result = result.str.cat(dataset['net'])
        result = result.str.cat(dataset['mem'])
        dataset.insert(0, 'label', result)
        dataset.to_csv('clusteringresult.csv')

    def labelling(self, data):
        """
        labelling the data from csv
        :param data:  the data
        """
        cpu = joblib.load(os.path.join(self.model_path, 'cpu_clu.m'))
        io_data = joblib.load(os.path.join(self.model_path, 'io_clu.m'))
        net = joblib.load(os.path.join(self.model_path, 'net_clu.m'))
        mem = joblib.load(os.path.join(self.model_path, 'mem_clu.m'))

        data = pd.DataFrame(data)

        cpu_util = pd.concat([data.iloc[:, 8], data.iloc[:, 45]], axis=1, join='inner')
        io_util = pd.concat([data.iloc[:, 3], data.iloc[:, 19]], axis=1, join='inner')
        net_util = [[x] for x in data.iloc[:, 25]]
        mem_total = [[x] for x in data.iloc[:, 29]]

        cpred = Counter(cpu.predict(cpu_util)).most_common(1)[0]
        ipred = Counter(io_data.predict(io_util)).most_common(1)[0]
        npred = Counter(net.predict(net_util)).most_common(1)[0]
        mpred = Counter(mem.predict(mem_total)).most_common(1)[0]

        print("The clustering result is", cpred[0], ipred[0], npred[0], mpred[0])
        print("The accuracy of the label prediction are ", cpred[1] / len(data),
              ipred[1] / len(data), npred[1] / len(data), mpred[1] / len(data))
        return [cpred[0], ipred[0], npred[0], mpred[0]]

    def svm_clf(self, clfpath, kernel):
        """
        svm_clf: support vector machine classifier
        """
        x_train, x_test, y_train, y_test = tts(self.x_axis, self.y_axis, test_size=0.3)

        rbf = svm.SVC(kernel=kernel, C=200)
        rbf.fit(x_train, y_train)
        rbf_score = rbf.score(x_test, y_test)
        print("the accuracy of rbf classification is %f" % rbf_score)
        joblib.dump(rbf, clfpath)

    def ada_clf(self, clfpath):
        """
        ada_clf: Adaptive Boosting classifier
        """
        x_train, x_test, y_train, y_test = tts(self.x_axis, self.y_axis, test_size=0.3)
        adaboost = AdaBoostClassifier(n_estimators=1000, learning_rate=0.05)
        adaboost.fit(x_train, y_train)
        adaboost_score = adaboost.score(x_test, y_test)
        print("the accuracy of adaboost is %f" % adaboost_score)
        print("the feature importances of this classifier are", adaboost.feature_importances_)
        joblib.dump(adaboost, clfpath)

    def xgb_clf(self, clfpath):
        """
        xgb_clf: XGBoost classifier
        """
        x_train, x_test, y_train, y_test = tts(self.x_axis, self.y_axis, test_size=0.3)
        model = XGBClassifier(learning_rate=0.1, n_estimators=400, max_depth=6,
                              min_child_weight=0.5, gamma=0.01, subsample=1, colsample_btree=1,
                              scale_pos_weight=1, random_state=27, slient=0, alpha=100)
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        print("the accuracy of xgboost is %f" % accuracy_score(y_test, y_pred))
        print("the feature importances of this classifier are", model.feature_importances_)
        joblib.dump(model, clfpath)

    def train(self, data_path):
        """
        train the data from csv
        :param data:  the data path
        """
        self.parsing(os.path.join(data_path, "*.csv"))
        self.y_axis = self.encoder.fit_transform(self.dataset.iloc[:, -1])
        joblib.dump(self.encoder, os.path.join(self.model_path, "encoder.pkl"))

        self.parsing(os.path.join(data_path, "*0100.csv"))
        self.x_axis = self.scaler.fit_transform(self.dataset.iloc[:, :-1])
        self.y_axis = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, os.path.join(self.model_path, "io_scaler.pkl"))
        self.svm_clf(os.path.join(self.model_path, "io_clf.m"), 'sigmoid')

        self.parsing(os.path.join(data_path, "*0010.csv"))
        self.x_axis = self.scaler.fit_transform(self.dataset.iloc[:, :-1])
        self.y_axis = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, os.path.join(self.model_path, "net_scaler.pkl"))
        self.svm_clf(os.path.join(self.model_path, "net_clf.m"), 'sigmoid')

        self.parsing(os.path.join(data_path, "*1000.csv"))
        self.x_axis = self.scaler.fit_transform(self.dataset.iloc[:, :-1])
        self.y_axis = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, os.path.join(self.model_path, "cpu_scaler.pkl"))
        self.xgb_clf(os.path.join(self.model_path, "cpu_clf.m"))

        self.parsing(os.path.join(data_path, "*1001.csv"))
        self.x_axis = self.scaler.fit_transform(self.dataset.iloc[:, :-1])
        self.y_axis = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, os.path.join(self.model_path, "cpumem_scaler.pkl"))
        self.svm_clf(os.path.join(self.model_path, "cpumem_clf.m"), 'rbf')

        self.parsing(os.path.join(data_path, "*1100.csv"))
        self.x_axis = self.scaler.fit_transform(self.dataset.iloc[:, :-1])
        self.y_axis = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, os.path.join(self.model_path, "cpuio_scaler.pkl"))
        self.svm_clf(os.path.join(self.model_path, "cpuio_clf.m"), 'rbf')

        self.parsing(os.path.join(data_path, "*1010.csv"))
        self.x_axis = self.scaler.fit_transform(self.dataset.iloc[:, :-1])
        self.y_axis = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, os.path.join(self.model_path, "cpunet_scaler.pkl"))
        self.svm_clf(os.path.join(self.model_path, "cpunet_clf.m"), 'rbf')

        self.parsing(os.path.join(data_path, "*1101.csv"))
        self.x_axis = self.scaler.fit_transform(self.dataset.iloc[:, :-1])
        self.y_axis = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, os.path.join(self.model_path, "cpuiomem_scaler.pkl"))
        self.svm_clf(os.path.join(self.model_path, "cpuiomem_clf.m"), 'rbf')

        self.parsing(os.path.join(data_path, "*1011.csv"))
        self.x_axis = self.scaler.fit_transform(self.dataset.iloc[:, :-1])
        self.y_axis = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, os.path.join(self.model_path, "cpunetmem_scaler.pkl"))
        self.svm_clf(os.path.join(self.model_path, "cpunetmem_clf.m"), 'rbf')

    def identify(self, data):
        """
        identify the workload_type according to input data
        :param data:  input data
        """
        data = pd.DataFrame(data)
        data = data.drop([28, 41, 42, 43, 44, 57, 58], axis=1)
        label = self.labelling(data)

        encoder_path = os.path.join(self.model_path, 'encoder.pkl')

        io_scaler = os.path.join(self.model_path, 'io_scaler.pkl')
        net_scaler = os.path.join(self.model_path, 'net_scaler.pkl')
        cpu_scaler = os.path.join(self.model_path, 'cpu_scaler.pkl')
        cpuio_scaler = os.path.join(self.model_path, 'cpuio_scaler.pkl')
        cpuiomem_scaler = os.path.join(self.model_path, 'cpuiomem_scaler.pkl')
        cpunet_scaler = os.path.join(self.model_path, 'cpunet_scaler.pkl')
        cpumem_scaler = os.path.join(self.model_path, 'cpumem_scaler.pkl')
        cpunetmem_scaler = os.path.join(self.model_path, 'cpunetmem_scaler.pkl')

        io_clf = os.path.join(self.model_path, 'io_clf.m')
        net_clf = os.path.join(self.model_path, 'net_clf.m')
        cpu_clf = os.path.join(self.model_path, 'cpu_clf.m')
        cpumem_clf = os.path.join(self.model_path, 'cpumem_clf.m')
        cpuio_clf = os.path.join(self.model_path, 'cpuio_clf.m')
        cpunet_clf = os.path.join(self.model_path, 'cpunet_clf.m')
        cpuiomem_clf = os.path.join(self.model_path, 'cpuiomem_clf.m')
        cpunetmem_clf = os.path.join(self.model_path, 'cpunetmem_clf.m')

        if label == [0, 0, 0, 0]:
            resourcelimit = " "
            print("The workload has been identified as non-intensive type")
            return resourcelimit, "default", 1
        if label == [0, 0, 0, 1]:
            resourcelimit = "io"
            print("The workload has been identified as mem-intensive type")
            return resourcelimit, "in-memory_computing", 1
        if label == [0, 0, 1, 0]:
            resourcelimit = "network"
            scaler = joblib.load(net_scaler)
            data = scaler.transform(data)
            print("The workload has been identified as network-intensive type")
            model = joblib.load(net_clf)
            result = model.predict(data)
        elif label == [0, 1, 0, 0]:
            resourcelimit = "io"
            scaler = joblib.load(io_scaler)
            data = scaler.transform(data)
            print("The workload has been identified as io-intensive type")
            model = joblib.load(io_clf)
            result = model.predict(data)
        elif label == [1, 0, 0, 0]:
            resourcelimit = "cpu"
            scaler = joblib.load(cpu_scaler)
            data = scaler.transform(data)
            print("The workload has been identified as cpu-intensive type")
            model = joblib.load(cpu_clf)
            result = model.predict(data)
        elif label == [1, 0, 0, 1]:
            resourcelimit = "cpu,memory"
            scaler = joblib.load(cpumem_scaler)
            data = scaler.transform(data)
            print("The workload has been identified as cpu-mem-intensive type")
            model = joblib.load(cpumem_clf)
            result = model.predict(data)
        elif label == [1, 0, 1, 0]:
            resourcelimit = "cpu,io"
            scaler = joblib.load(cpunet_scaler)
            data = scaler.transform(data)
            print("The workload has been identified as cpu-net-intensive type")
            model = joblib.load(cpunet_clf)
            result = model.predict(data)
        elif label == [1, 0, 1, 1]:
            resourcelimit = "cpu,network,memory"
            scaler = joblib.load(cpunetmem_scaler)
            data = scaler.transform(data)
            print("The workload has been identified as cpu-net-mem-intensive type")
            model = joblib.load(cpunetmem_clf)
            result = model.predict(data)
        elif label == [1, 1, 0, 0]:
            resourcelimit = "cpu,io"
            scaler = joblib.load(cpuio_scaler)
            data = scaler.transform(data)
            print("The workload has been identified as cpu-io-intensive type")
            model = joblib.load(cpuio_clf)
            result = model.predict(data)
        elif label == [1, 1, 0, 1]:
            resourcelimit = "cpu,io,memory"
            scaler = joblib.load(cpuiomem_scaler)
            data = scaler.transform(data)
            print("The workload has been identified as cpu-io-mem-intensive type")
            model = joblib.load(cpuiomem_clf)
            result = model.predict(data)
        elif label == [1, 1, 1, 1]:
            resourcelimit = "cpu,io,network,memory"
            print("The workload has been identified as cpu-io-net-mem-intensive type")
            return resourcelimit, "big_database", 1
        else:
            resourcelimit = ""
            print("Error: Unsupported classifier type")
            return resourcelimit, "default", 0

        encoder = joblib.load(encoder_path)
        result = encoder.inverse_transform(result)
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
        self.parsing(data_path)
        self.x_axis = self.scaler.fit_transform(self.dataset.iloc[:, :-1])
        self.y_axis = self.encoder.fit_transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, os.path.join(dirname, scalername))
        joblib.dump(self.encoder, os.path.join(dirname, encodername))

        class_num = len(self.encoder.classes_)
        if class_num == 1:
            self.y_axis[-1] = self.y_axis[-1] + 1
        self.svm_clf(custom_path, 'rbf')

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
