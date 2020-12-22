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
# Create: 2020-09-29

"""
This class is used to statistic the data
"""

import glob
import pandas as pd

class WorkloadStatistic:
    """statistics"""

    def __init__(self):
        self.statistics = None
        self.dataset = None
        self.data_features = ['CPU.STAT.usr', 'CPU.STAT.nice', 'CPU.STAT.sys', 'CPU.STAT.iowait',
                              'CPU.STAT.irq', 'CPU.STAT.soft', 'CPU.STAT.steal', 'CPU.STAT.guest',
                              'CPU.STAT.util', 'CPU.STAT.cutil', 'STORAGE.STAT.rs',
                              'STORAGE.STAT.ws', 'STORAGE.STAT.rMBs', 'STORAGE.STAT.wMBs',
                              'STORAGE.STAT.rrqm', 'STORAGE.STAT.wrqm', 'STORAGE.STAT.rareq-sz',
                              'STORAGE.STAT.wareq-sz', 'STORAGE.STAT.r_await',
                              'STORAGE.STAT.w_await', 'STORAGE.STAT.util', 'STORAGE.STAT.aqu-sz',
                              'NET.STAT.rxkBs', 'NET.STAT.txkBs', 'NET.STAT.rxpcks',
                              'NET.STAT.txpcks', 'NET.STAT.ifutil', 'NET.ESTAT.errs',
                              'NET.ESTAT.util', 'MEM.BANDWIDTH.Total_Util', 'PERF.STAT.IPC',
                              'PERF.STAT.CACHE-MISS-RATIO', 'PERF.STAT.MPKI',
                              'PERF.STAT.ITLB-LOAD-MISS-RATIO', 'PERF.STAT.DTLB-LOAD-MISS-RATIO',
                              'PERF.STAT.SBPI', 'PERF.STAT.SBPC', 'MEM.VMSTAT.procs.b',
                              'MEM.VMSTAT.io.bo', 'MEM.VMSTAT.system.in', 'MEM.VMSTAT.system.cs',
                              'MEM.VMSTAT.util.swap', 'MEM.VMSTAT.util.cpu', 'MEM.VMSTAT.procs.r',
                              'SYS.TASKS.procs', 'SYS.TASKS.cswchs', 'SYS.LDAVG.runq-sz',
                              'SYS.LDAVG.plist-sz', 'SYS.LDAVG.ldavg-1', 'SYS.LDAVG.ldavg-5',
                              'SYS.FDUTIL.fd-util', 'MEM.VMSTAT.memory.swpd']

    @staticmethod
    def abnormal_detection(x_axis):
        """
        3-sigma detect abnormal data points
        :param x_axis: the input data
        :returns result: filtered data
        """
        bool_normal = (x_axis.mean() - 3 * x_axis.std() <= x_axis) & \
                      (x_axis <= x_axis.mean() + 3 * x_axis.std())
        result = x_axis[bool_normal]
        return result

    def parsing(self, data_path, header=0):
        """
        parse the data from csv
        :param data_path:  the path of csv
        :param header:  default 0
        """
        df_content = []
        csvfiles = glob.glob(data_path)
        selected_cols = list(self.data_features)
        selected_cols.append('workload.type')
        selected_cols.append('workload.appname')

        for csv in csvfiles:
            data = pd.read_csv(csv, index_col=None, header=header, usecols=selected_cols)
            data[self.data_features] = self.abnormal_detection(data[self.data_features])
            df_content.append(data.dropna(axis=0))
        self.dataset = pd.concat(df_content, sort=False)

    def statistic(self, data_path):
        """
        :param data_path: the path of csv
        """
        self.parsing(data_path, 0)
        self.statistics = pd.DataFrame()
        for workload_appname, name_group in self.dataset.groupby('workload.appname'):
            data = name_group.iloc[:, :-2]
            mean = data.mean().to_frame().T
            std = data.std().to_frame().T
            mean['workload_appname'] = workload_appname
            mean['data_type'] = "mean"
            std['workload_appname'] = workload_appname
            std['data_type'] = "std"
            self.statistics = pd.concat([self.statistics, std, mean], ignore_index=True)


class DetectItem:
    """detection class"""

    def __init__(self, statistics, data_features):
        self.data_features = data_features
        self.statistics = statistics

    def detection(self, detect_path, workload_appname, header=0):
        """
        :param detect_path: detect dataset path
        :param workload_appname: the workload app name
        :param header: default 0
        :return: statistics of detecting data
        """
        dataset = pd.read_csv(detect_path, index_col=None, header=header)
        val = dataset.mean()
        return self.df_detection(val, workload_appname)

    def df_detection(self, val, workload_appname):
        """
        :param val: statistics
        :param workload_appname: the workload app name
        :return: detection result
        """
        statistic = self.statistics[self.statistics['workload_appname'] == workload_appname]
        mean = statistic[statistic['data_type'] == 'mean']
        std = statistic[statistic['data_type'] == 'std']
        result = ""
        for item in self.data_features:
            temp = ""
            if val[item] > (mean[item].values + std[item].values * 3):
                temp = str(val[item]) + ">" + str(mean[item].values - std[item].values) + "," +\
                        str(mean[item].values + std[item].values) + "@"
            elif val[item] < (mean[item].values - std[item].values * 3):
                temp = str(val[item]) + "<" + str(mean[item].values - std[item].values) + "," +\
                        str(mean[item].values + std[item].values) + "@"
            if temp != "":
                result = result + str(item) + " " + temp
        return result
