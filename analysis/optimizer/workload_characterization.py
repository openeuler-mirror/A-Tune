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
import hashlib
import numpy as np
import pandas as pd
from sklearn import svm
from collections import Counter
from xgboost import XGBClassifier
from sklearn.cluster import KMeans
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split as tts
from sklearn.preprocessing import StandardScaler, LabelEncoder

class WorkloadCharacterization(object):
    def __init__(self, model_path):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.encoder = LabelEncoder()
        self.dataset = None
        self.X = None
        self.y = None

    def parsing(self, data_path):
        df = [ ]
        print (data_path)
        csvfiles = glob.glob(data_path)
        for csv in csvfiles:
            print ("file:", csv)
            data = pd.read_csv(csv, index_col=None, header=None)
            df.append(data)
            dataset = pd.concat(df)
        self.dataset = dataset
        return dataset

    def clustering(self, data_path):
        complete_path = os.path.join(data_path,"*.csv")
        self.parsing(complete_path)
        dataset = self.dataset.drop([28,41,42,43,44,57,58], axis=1)
        cpu_util = pd.concat([dataset.iloc[:,8], dataset.iloc[:,45]], axis=1, join='inner')
        io_util = pd.concat([dataset.iloc[:,3], dataset.iloc[:,19]], axis=1, join='inner')
        net_util = dataset.iloc[:,25]
        mem_total = dataset.iloc[:,29]

        cpu_path = os.path.join(self.model_path,'cpu_clu.m')
        io_path = os.path.join(self.model_path,'io_clu.m')
        net_path = os.path.join(self.model_path,'net_clu.m')
        mem_path = os.path.join(self.model_path,'mem_clu.m')

        cpu = KMeans(n_clusters=2)
        s = cpu.fit(cpu_util)
        joblib.dump(cpu, cpu_path)
        c_pred = cpu.predict(cpu_util)

        io = KMeans(n_clusters=2)
        s = io.fit(io_util)
        joblib.dump(io, io_path)
        i_pred = io.predict(io_util)

        net = KMeans(n_clusters=2)
        x= [[x] for x in net_util]
        s = net.fit(x)
        joblib.dump(net, net_path)
        n_pred = net.predict(x)

        mem = KMeans(n_clusters=2)
        x= [[x] for x in mem_total]
        s = mem.fit(x)
        joblib.dump(mem, mem_path)
        m_pred = mem.predict(x)

        result = pd.concat([pd.DataFrame(c_pred), pd.DataFrame(i_pred), pd.DataFrame(n_pred), pd.DataFrame(m_pred)], axis=1)
        cpu_result = result.iloc[:,0].map(lambda x:str(x))
        io_result = result.iloc[:,1].map(lambda x:str(x))
        net_result = result.iloc[:,2].map(lambda x:str(x))
        mem_result = result.iloc[:,3].map(lambda x:str(x))
        label = cpu_result.str.cat(io_result)
        label = label.str.cat(net_result)
        label = label.str.cat(mem_result)
        dataset.insert(0, 'label', label)
        dataset.to_csv('clusteringresult.csv')

    def labelling(self, data):
        cpu_path = os.path.join(self.model_path,'cpu_clu.m')
        io_path = os.path.join(self.model_path,'io_clu.m')
        net_path = os.path.join(self.model_path,'net_clu.m')
        mem_path = os.path.join(self.model_path,'mem_clu.m')

        cpu = joblib.load(cpu_path)
        io  = joblib.load(io_path)
        net = joblib.load(net_path)
        mem = joblib.load(mem_path)

        X = pd.DataFrame(data)

        cpu_util = pd.concat([X.iloc[:,8], X.iloc[:,45]], axis=1, join='inner') 
        io_util = pd.concat([X.iloc[:,3], X.iloc[:,19]], axis=1, join='inner')
        net_util = [[x] for x in X.iloc[:, 25]]
        mem_total = [[x] for x in X.iloc[:, 29]]

        ctype = cpu.predict(cpu_util)
        itype = io.predict(io_util)
        ntype = net.predict(net_util)
        mtype = mem.predict(mem_total)
        cpred = Counter(ctype).most_common(1)[0]
        ipred = Counter(itype).most_common(1)[0]
        npred = Counter(ntype).most_common(1)[0]
        mpred = Counter(mtype).most_common(1)[0]

        print ("The clustering result is", cpred[0], ipred[0], npred[0], mpred[0])
        print ("The accuracy of the label prediction are ", cpred[1]/len(data),
            ipred[1]/len(data), npred[1]/len(data), mpred[1]/len(data))
        return [cpred[0], ipred[0], npred[0], mpred[0]]

    def svm_clf(self, clfpath, kernel):
        X_train, X_test, y_train, y_test = tts(self.X, self.y, test_size=0.3)

        rbf = svm.SVC(kernel= kernel, C=200)
        rbf.fit(X_train, y_train)
        rbf_score = rbf.score(X_test, y_test)
        print ("the accuracy of rbf classification is %f" %rbf_score)
        joblib.dump(rbf, clfpath)

    def ada_clf(self, clfpath):
        X_train, X_test, y_train, y_test = tts(self.X, self.y, test_size=0.3)
        adaboost = AdaBoostClassifier(n_estimators=1000, learning_rate=0.05)
        adaboost.fit(X_train, y_train)
        adaboost_score = adaboost.score(X_test, y_test)
        print ("the accuracy of adaboost is %f" %adaboost_score)
        print ("the feature importances of this classifier are", adaboost.feature_importances_)
        joblib.dump(adaboost, clfpath)

    def xgb_clf(self, clfpath):
        X_train, X_test, y_train, y_test = tts(self.X, self.y, test_size=0.3)
        model = XGBClassifier(learning_rate=0.1, n_estimators=400, max_depth=6, min_child_weight = 0.5, gamma=0.01,
                            subsample=1, colsample_btree=1, scale_pos_weight=1, random_state=27, slient = 0, alpha=100)
        model.fit(X_train,y_train)
        y_pred = model.predict(X_test)
        print ("the accuracy of xgboost is %f" %accuracy_score(y_test,y_pred))
        print ("the feature importances of this classifier are", model.feature_importances_)
        joblib.dump(model, clfpath)

    def train(self, data_path):
        encoder_path = os.path.join(self.model_path,"encoder.pkl")
        complete_path = os.path.join(data_path,"*.csv")

        io_path = os.path.join(data_path,"*0100.csv")
        net_path = os.path.join(data_path,"*0010.csv")
        cpu_path = os.path.join(data_path,"*1000.csv")
        cpumem_path = os.path.join(data_path,"*1001.csv")
        cpuio_path = os.path.join(data_path,"*1100.csv")
        cpunet_path = os.path.join(data_path,"*1010.csv")
        cpuiomem_path = os.path.join(data_path,"*1101.csv")
        cpunetmem_path = os.path.join(data_path,"*1011.csv")

        io_clf = os.path.join(self.model_path,"io_clf.m")
        net_clf = os.path.join(self.model_path,"net_clf.m")
        cpu_clf = os.path.join(self.model_path,"cpu_clf.m")
        cpumem_clf = os.path.join(self.model_path,"cpumem_clf.m")
        cpuio_clf = os.path.join(self.model_path,"cpuio_clf.m")
        cpuiomem_clf = os.path.join(self.model_path,"cpuiomem_clf.m")
        cpunet_clf = os.path.join(self.model_path,"cpunet_clf.m")
        cpunetmem_clf = os.path.join(self.model_path,"cpunetmem_clf.m")

        io_scl = os.path.join(self.model_path,"io_scaler.pkl")
        net_scl = os.path.join(self.model_path,"net_scaler.pkl")
        cpu_scl = os.path.join(self.model_path,"cpu_scaler.pkl")
        cpumem_scl = os.path.join(self.model_path,"cpumem_scaler.pkl")
        cpuio_scl = os.path.join(self.model_path,"cpuio_scaler.pkl")
        cpuiomem_scl = os.path.join(self.model_path,"cpuiomem_scaler.pkl")
        cpunet_scl = os.path.join(self.model_path,"cpunet_scaler.pkl")
        cpunetmem_scl = os.path.join(self.model_path,"cpunetmem_scaler.pkl")
        
        self.parsing(complete_path)
        self.y = self.encoder.fit_transform(self.dataset.iloc[:, -1])
        joblib.dump(self.encoder, encoder_path)

        self.parsing(io_path)
        self.X = self.scaler.fit_transform(self.dataset.iloc[:,:-1])
        self.y = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, io_scl)
        self.svm_clf(io_clf, 'sigmoid')
        print ("The classifier for io-intensive workload has been generated.")

        self.parsing(net_path)
        self.X = self.scaler.fit_transform(self.dataset.iloc[:,:-1])
        self.y = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, net_scl)
        self.svm_clf(net_clf, 'sigmoid')
        print ("The classifier for net-intensive workload has been generated.")

        self.parsing(cpu_path)
        self.X = self.scaler.fit_transform(self.dataset.iloc[:,:-1])
        self.y = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, cpu_scl)
        self.xgb_clf(cpu_clf)
        print ("The classifier for cpu-intensive workload has been generated.")

        self.parsing(cpumem_path)
        self.X = self.scaler.fit_transform(self.dataset.iloc[:,:-1])
        self.y = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, cpumem_scl)
        self.svm_clf(cpumem_clf, 'rbf')
        print ("The classifier for cpumem-intensive workload has been generated.")

        self.parsing(cpuio_path)
        self.X = self.scaler.fit_transform(self.dataset.iloc[:,:-1])
        self.y = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, cpuio_scl)
        self.svm_clf(cpuio_clf, 'rbf')
        print ("The classifier for cpuio-intensive workload has been generated.")

        self.parsing(cpunet_path)
        self.X = self.scaler.fit_transform(self.dataset.iloc[:,:-1])
        self.y = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, cpunet_scl)
        self.svm_clf(cpunet_clf, 'rbf')
        print ("The classifier for cpunet-intensive workload has been generated.")

        self.parsing(cpuiomem_path)
        self.X = self.scaler.fit_transform(self.dataset.iloc[:,:-1])
        self.y = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, cpuiomem_scl)
        self.svm_clf(cpuiomem_clf, 'rbf')
        print ("The classifier for cpuiomem-intensive workload has been generated.")

        self.parsing(cpunetmem_path)
        self.X = self.scaler.fit_transform(self.dataset.iloc[:,:-1])
        self.y = self.encoder.transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, cpunetmem_scl)
        self.svm_clf(cpunetmem_clf, 'rbf')
        print ("The classifier for cpunetmem-intensive workload has been generated.")

    def identify(self, x):
        x = pd.DataFrame(x)
        x = x.drop([28,41,42,43,44,57,58], axis=1)
        l = self.labelling(x)

        encoder_path = os.path.join(self.model_path,'encoder.pkl')

        io_scaler = os.path.join(self.model_path,'io_scaler.pkl')
        net_scaler = os.path.join(self.model_path,'net_scaler.pkl')
        cpu_scaler = os.path.join(self.model_path,'cpu_scaler.pkl')
        cpuio_scaler = os.path.join(self.model_path,'cpuio_scaler.pkl')
        cpuiomem_scaler = os.path.join(self.model_path,'cpuiomem_scaler.pkl')
        cpunet_scaler = os.path.join(self.model_path,'cpunet_scaler.pkl')
        cpumem_scaler = os.path.join(self.model_path,'cpumem_scaler.pkl')
        cpunetmem_scaler = os.path.join(self.model_path,'cpunetmem_scaler.pkl')

        io_clf = os.path.join(self.model_path,'io_clf.m')
        net_clf = os.path.join(self.model_path,'net_clf.m')
        cpu_clf = os.path.join(self.model_path,'cpu_clf.m')
        cpumem_clf = os.path.join(self.model_path,'cpumem_clf.m')
        cpuio_clf = os.path.join(self.model_path,'cpuio_clf.m')
        cpunet_clf = os.path.join(self.model_path,'cpunet_clf.m')
        cpuiomem_clf = os.path.join(self.model_path,'cpuiomem_clf.m')
        cpunetmem_clf = os.path.join(self.model_path,'cpunetmem_clf.m')

        if l == [0, 0, 0, 0]:
            resourcelimit = " "
            print ("The workload has been identified as non-intensive type")
            return resourcelimit, "default", 1
        elif l == [0, 0, 0, 1] :
            resourcelimit = "io"
            print ("The workload has been identified as mem-intensive type")
            return resourcelimit, "in-memory_computing", 1
        elif l == [0, 0, 1, 0] :
            resourcelimit = "network"
            scaler = joblib.load(net_scaler)
            x = scaler.transform(x)         
            print ("The workload has been identified as network-intensive type")
            model = joblib.load(net_clf)
            result = model.predict(x)
        elif l == [0, 1, 0, 0] :
            resourcelimit = "io"
            scaler = joblib.load(io_scaler)
            x = scaler.transform(x)         
            print ("The workload has been identified as io-intensive type")
            model = joblib.load(io_clf)
            result = model.predict(x)
        elif l == [1, 0, 0, 0]:
            resourcelimit = "cpu"
            scaler = joblib.load(cpu_scaler)
            x = scaler.transform(x)         
            print ("The workload has been identified as cpu-intensive type")
            model = joblib.load(cpu_clf)
            result = model.predict(x)
        elif l == [1, 0, 0, 1] :
            resourcelimit = "cpu,memory"
            scaler = joblib.load(cpumem_scaler)
            x = scaler.transform(x)
            print ("The workload has been identified as cpu-mem-intensive type")
            model = joblib.load(cpumem_clf)
            result = model.predict(x)
        elif l == [1, 0, 1, 0] :
            resourcelimit = "cpu,io"
            scaler = joblib.load(cpunet_scaler)
            x = scaler.transform(x)
            print ("The workload has been identified as cpu-net-intensive type")
            model = joblib.load(cpunet_clf)
            result = model.predict(x)
        elif l == [1, 0, 1, 1] :
            resourcelimit = "cpu,network,memory"
            scaler = joblib.load(cpunetmem_scaler)
            x = scaler.transform(x)
            print ("The workload has been identified as cpu-net-mem-intensive type")
            model = joblib.load(cpunetmem_clf)
            result = model.predict(x)
        elif l == [1, 1, 0, 0]:
            resourcelimit = "cpu,io"
            scaler = joblib.load(cpuio_scaler)
            x = scaler.transform(x)
            print ("The workload has been identified as cpu-io-intensive type")
            model = joblib.load(cpuio_clf)
            result = model.predict(x)
        elif l == [1, 1, 0, 1] :
            resourcelimit = "cpu,io,memory"
            scaler = joblib.load(cpuiomem_scaler)
            x = scaler.transform(x)
            print ("The workload has been identified as cpu-io-mem-intensive type")
            model = joblib.load(cpuiomem_clf)
            result = model.predict(x)
        elif l ==[1, 1, 1, 1]:
            resourcelimit = "cpu,io,network,memory"
            print ("The workload has been identified as cpu-io-net-mem-intensive type")
            return resourcelimit, "big_database", 1            
        else:
            resourcelimit = ""
            print ("Error: Unsupported classifier type")
            return resourcelimit, "default", 0

        encoder = joblib.load(encoder_path)
        result = encoder.inverse_transform(result)
        print (result)
        prediction = Counter(result).most_common(1)[0]
        confidence = prediction[1]/len(result)
        if confidence > 0.5:
            return resourcelimit, prediction[0], confidence
        else:
            return resourcelimit, "default", confidence

    def retrain(self, data_path, custom_path):
        custom_path = os.path.abspath(custom_path)
        (dirname, filename) = os.path.split(custom_path)
        (modelname, extension) = os.path.splitext(filename)
        scalername = modelname + '_scaler.pkl'
        encodername = modelname + '_encoder.pkl'

        data_path = os.path.join(data_path,"*.csv")
        self.parsing(data_path)
        self.X = self.scaler.fit_transform(self.dataset.iloc[:, :-1])
        self.y = self.encoder.fit_transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, os.path.join(dirname, scalername))
        joblib.dump(self.encoder, os.path.join(dirname, encodername))

        class_num = len(self.encoder.classes_)
        if class_num == 1:
            self.y[-1] = self.y[-1] + 1
        self.svm_clf(custom_path)

    def reidentify(self, x, custom_path):
        custom_path = os.path.abspath(custom_path)
        (dirname, filename) = os.path.split(custom_path)
        (modelname, extension) = os.path.splitext(filename)
        scalername = modelname + '_scaler.pkl'
        encodername = modelname + '_encoder.pkl'

        scaler = joblib.load(os.path.join(dirname, scalername))
        encoder = joblib.load(os.path.join(dirname, encodername))
        model = joblib.load(custom_path)
        
        x = scaler.transform(x)
        result = model.predict(x)
        result = encoder.inverse_transform(result)
        print (result)

        prediction = Counter(result).most_common(1)[0]
        confidence = prediction[1]/len(result)
        if confidence > 0.5:
            return prediction[0], confidence
        else:
            return "default", confidence