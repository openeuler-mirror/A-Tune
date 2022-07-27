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
# Create: 2022-04-06
"""
This class is used to perform  genetic algorithm tuning and generate optimized profile
"""
import logging
import copy
import numpy as np
import geatpy as ea
LOGGER = logging.getLogger(__name__)
class GATuning:
    """ genetic algorithm tuning  """
    def __init__(self,knobs,child_conn):
        dict_para = []
        para_lb = []
        para_ub= []
        para_type = []
        para_name = []
        pt = []
        for p_nob in knobs:
            para_name.append(p_nob['name'])
            pt.append(p_nob['dtype'])
            if p_nob['dtype'] =='string':
                dict_para.append(p_nob['options'])
                opt_num = len(p_nob['options'])
                para_lb.append(0)
                para_ub.append(opt_num-1)
                para_type.append(int(0))
            if p_nob['dtype'] == 'int':
                r_range = p_nob['range']
                if 'step' in p_nob.keys():
                    step = 1 if p_nob['step'] < 1 else p_nob['step']
                if r_range is not None:
                    length = len(r_range) if len(r_range) % 2 == 0 else len(r_range) - 1
                    for i in range(0, length, 2):
                        tmpset = list(np.arange(r_range[i], r_range[i + 1] + 1, step=step))
                dict_para.append(tmpset)
                para_lb.append(0)
                para_ub.append(len(tmpset)-1)
                para_type.append(int(0))
            if p_nob['dtype'] == 'float':
                dict_para.append([])
                r_range = p_nob['range']
                para_lb.append(r_range[0])
                para_ub.append(r_range[1])
                para_type.append(int(1))
        self._para_name = para_name

        self._dict_para = dict_para
        self._pt = pt
        self._para_lb = para_lb
        self._para_ub = para_ub
        self._para_type = para_type
        self._child_conn = child_conn

    def evalVars(self,Vars):
        """ fitness function for genetic algorithm tuning  """
        iter_result ={}
        params = {}
        performance_list = []
        for m in range(Vars.shape[0]):
            for i in range(Vars.shape[1]):
        # for i,val in enumerate(Vars):
                if self._pt[i] == "string" :
                    params[self._para_name[i]] = self._dict_para[i][int(Vars[m,i])]
                if self._pt[i] == 'int':
                    params[self._para_name[i]] = int(self._dict_para[i][int(Vars[m,i])])
                if self._pt[i] == 'float':
                    params[self._para_name[i]] = float(Vars[m,i])
            iter_result['param'] = params
            self._child_conn.send(iter_result)
            result = self._child_conn.recv()
            x_num = 0.0
            eval_list = result.split(',')
            for value in eval_list:
                num = float(value)
                x_num = x_num + num
            performance = x_num
            performance_list.append([performance])

        return np.array(performance_list)
    def GA(self):
        """ genetic algorithm tuning manager """
        problem = ea.Problem(name='genetic algorithm for atune',
                            M=1,
                            maxormins=[-1],
                            Dim=int(len(self._para_lb)),
                            varTypes = self._para_type,
                            lb = self._para_lb,
                            ub = self._para_ub,
                            evalVars=self.evalVars)

        algorithm = ea.soea_SEGA_templet(problem,
                                        ea.Population(Encoding='RI', NIND=5),
                                        MAXGEN=10,
                                        logTras=1,
                                        trappedValue=1e-6,
                                        maxTrappedCount=10)

        res = ea.optimize(algorithm, seed=1, verbose=False, drawing=0, outputMsg=False, drawLog=False)
        best_result_list = res['Vars'].tolist()[0]
        best_result = {}
        for i,val in enumerate(best_result_list):
            if self._pt[i] == "string" :
                best_result[self._para_name[i]] = self._dict_para[i][int(val)]
            if self._pt[i] == 'int':
                best_result[self._para_name[i]] = int(val)
            if self._pt[i] == 'float':
                best_result[self._para_name[i]] = float(val)
        return best_result
