# Copyright (c) 2022 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   zhaoyanjun
# @Contact   :   zhao-yanjun@qq.com
# @Date      :   2022/10/10
# @License   :   Mulan PSL v2
# #############################################

import torch
import os
import random
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import numpy as np
import collections
import numbers
import math
import pandas as pd
from sklearn.preprocessing import StandardScaler
import pickle

class DataSegLoader(object):
    '''load data and get data segment'''
    def __init__(self, train_path, test_path, label_path, data_name, win_size, step, mode = "train"):
        self.mode = mode
        self.step = step
        self.win_size = win_size
        self.scaler = StandardScaler()

        train_data = pd.read_csv(train_path + str(data_name))
        test_data = pd.read_csv(test_path + str(data_name))
        train_data = train_data.values
        test_data = test_data.values

        train_data = self.scaler.fit_transform(train_data)
        test_data = self.scaler.fit_transform(test_data)

        self.train = train_data
        self.test  = test_data
        data_len = len(self.train)
        self.val = self.test
        label = pd.read_csv(label_path + str(data_name))
        labels = label['label'].values
        self.test_labels = labels

    def __len__(self):
        '''get data length'''

        if self.mode == "train":
            return (self.train.shape[0] - self.win_size) // self.step + 1
        elif (self.mode == 'thre'):
            return (self.val.shape[0] - self.win_size) // self.win_size + 1
        else:
            return (self.test.shape[0] - self.win_size) // self.step + 1

    def __getitem__(self, index):
        '''get data segment'''

        index = index * self.step
        if self.mode == "train":
            return np.float32(self.train[index:index + self.win_size])
        elif (self.mode == 'val'):
            return np.float32(self.val[index:index + self.win_size]), np.float32(self.test_labels[0:self.win_size])
        elif (self.mode == 'test'):
            return np.float32(self.test[index:index + self.win_size]), np.float32(
                self.test_labels[index:index + self.win_size])
        elif (self.mode == 'thre'):
            segment_index = index // self.step * self.win_size
            segment_end = segment_index + self.win_size
            return np.float32(self.test[segment_index:segment_end]), np.float32(self.test_labels[segment_index:segment_end])
        return None

def get_loader_segment(train_path, test_path, label_path, batch_size, file_name = None, win_size = 100, step = 1, mode = 'train'):
    '''load data and return data segment'''
    dataset = DataSegLoader(train_path, test_path, label_path, file_name, win_size, 1, mode)
    
    if mode == 'train':
        shuffle = True
    else:
        shuffle = False

    data_loader = DataLoader(dataset = dataset,
                             batch_size = batch_size,
                             shuffle = shuffle,
                             num_workers = 0)
    return data_loader
