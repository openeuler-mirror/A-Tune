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
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import numpy as np
import pandas as pd
import os
import time
from Anomaly_Transformer.model.AnomalyTransformer import AnomalyTransformer
from data_loader import get_loader_segment
from sklearn.metrics import accuracy_score

def my_kl_loss(p, q, loss_bias):
    '''calculate my_kl_loss with loss_bias'''
    res = p * (torch.log(p + loss_bias) - torch.log(q + loss_bias))
    return torch.mean(torch.sum(res, dim = -1), dim = 1)


def adjust_learning_rate(optimizer, epoch, lr_):
    '''adjust learning_rate during the training'''
    lr_adjust = {epoch: lr_ * (0.5 ** ((epoch - 1) // 1))}
    if epoch in lr_adjust.keys():
        lr = lr_adjust[epoch]
        for param_group in optimizer.param_groups:
            param_group['lr'] = lr
        print('Updating learning rate to {}'.format(lr))


class EarlyStopping:
    '''stop the training earlier according to the training result'''
    def __init__(self, patience, model_save_file, verbose = False, dataset_name=''):
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.best_score2 = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.val_loss2_min = np.Inf
        self.dataset = dataset_name
        self.model_save_file = model_save_file
        self.model_check = True

    def __call__(self, val_loss, val_loss2, model, path):
        '''check the EarlyStopping conditions during the training'''
        score = -val_loss
        score2 = -val_loss2
        if self.best_score is None:
            self.best_score = score
            self.best_score2 = score2
            self.save_checkpoint(val_loss, val_loss2, model, path)
        elif score < self.best_score or score2 < self.best_score2 :
            self.counter += 1
            if not self.counter < self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.best_score2 = score2
            self.save_checkpoint(val_loss, val_loss2, model, path)
            self.counter = 0

    def save_checkpoint(self, val_loss, val_loss2, model, path):
        '''save the model into checkpoint'''
        model_checkpoint_path = os.path.join(path, str(self.dataset) + self.model_save_file)
        if self.verbose:
            print(f'Validation loss decreased ({self.val_loss_min:.6f} --> {val_loss:.6f}).  Saving model ...')
        if self.model_check :
            torch.save(model.state_dict(), model_checkpoint_path)
        self.val_loss_min = val_loss
        self.val_loss2_min = val_loss2


class Detection(object):
    '''anomaly detection'''
    DEFAULTS = {}

    def __init__(self, config):

        self.__dict__.update(Detection.DEFAULTS, **config)
        self.build_model()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.criterion = nn.MSELoss()

    def build_model(self):
        self.model = AnomalyTransformer(win_size = self.win_size, enc_in = self.input_c, c_out = self.output_c, e_layers = 3)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr = self.lr)

        if torch.cuda.is_available():
            self.model.cuda()

    def detect(self, mode):
        '''train the model with mutiple datasets and share the model'''
        if mode == "train":
            dataset_list = os.listdir(self.train_path)
        elif mode == "test":
            dataset_list = os.listdir(self.test_path)
        for dataset in dataset_list:
            print(str(dataset))
            self.train_loader = get_loader_segment(self.train_path, self.test_path, self.label_path, file_name = str(dataset), 
                                    batch_size = self.batch_size, win_size = self.win_size, mode = 'train')
            self.vali_loader = get_loader_segment(self.train_path, self.test_path, self.label_path, file_name=str(dataset), 
                                    batch_size = self.batch_size, win_size = self.win_size, mode = 'val')
            self.test_loader = get_loader_segment(self.train_path, self.test_path, self.label_path,  file_name=str(dataset),   
                                    batch_size = self.batch_size, win_size = self.win_size, mode = 'test')
            self.thre_loader = get_loader_segment(self.train_path, self.test_path, self.label_path, file_name = str(dataset), 
                                    batch_size = self.batch_size, win_size = self.win_size, mode = 'thre')
            if mode == "train":
                self.train()
            elif mode == "test":
                accuracy, delay_time, thresh = self.test()
                performance.append([accuracy, delay_time, thresh])
        if mode == "test":
            mean_accuracy=np.mean([i[0] for i in performance])
            mean_delay_time=np.mean([i[1] for i in performance])
            mean_thresh=np.mean([i[2] for i in performance])
            print('Final mean performance of 40 datasets:')
            print("Mean_thresh_score is {:0.5f}".format(mean_thresh))
            print("{:0.2%} of Anomaly status is detected!".format(mean_accuracy))
    
    def vali(self, vali_loader):
        '''validate the model'''
        self.model.eval()

        loss_a = []
        loss_b = []
        for i, (input_data, _) in enumerate(vali_loader):
            series_loss, prior_loss, rec_loss = cal_loss(self, input_data)

            loss_a.append((rec_loss - self.k * series_loss).item())
            loss_b.append((rec_loss + self.k * prior_loss).item())

        return np.average(loss_a), np.average(loss_b)


    def train(self):
        '''train the model with single dataset'''
        time_now = time.time()
        path = self.model_save_path
        
        if not os.path.exists(path):
            os.makedirs(path)
        early_stopping = EarlyStopping(patience = self.patience, verbose = True, dataset_name = self.dataset, model_save_file = self.model_save_file)
        train_steps = len(self.train_loader)
        
        #share model for 40datasets of AIops
        model_path = os.path.join(str(path), str(self.dataset) + self.model_save_file)
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path))  
        
        for epoch in range(self.num_epochs):
            train_loss_list = []

            epoch_time = time.time()
            
            self.model.train()
            for i, input_data in enumerate(self.train_loader):

                self.optimizer.zero_grad()
                series_loss, prior_loss, rec_loss = cal_loss(self, input_data)

                train_loss_list.append((rec_loss - self.k * series_loss).item())

                # Minimax strategy
                loss1 = rec_loss - self.k * series_loss
                loss1.backward(retain_graph=True)
                self.optimizer.step()

                loss2 = rec_loss + self.k * prior_loss
                loss2.backward()
                self.optimizer.step()

            train_loss = np.mean(train_loss_list)
            validate_loss1, validate_loss2 = self.vali(self.test_loader)
            
            print("Epoch: {0}, Steps: {1} | Train Loss: {2:.7f} Vali Loss: {3:.7f} ".format(
                    epoch + 1, train_steps, train_loss, validate_loss1))
            print("cost time: {}".format(time.time() - epoch_time))

            early_stopping(validate_loss1, validate_loss2, self.model, path)

            if early_stopping.early_stop:
                print("Early stopping")
                break

            adjust_learning_rate(self.optimizer, epoch + 1, self.lr)
    
    def cal_loss(self, input_data):
        # calculate Association discrepancy
        input = input_data.float()
        output, series, prior, _ = self.model(input.to(self.device))

        for u,item in enumerate(prior):

            prior_p = prior[u] / torch.unsqueeze(torch.sum(prior[u], dim = -1), dim = -1).repeat(1, 1, 1, self.win_size)
            series_p = (prior[u] / torch.unsqueeze(torch.sum(prior[u], dim = -1), dim = -1).repeat(1, 1, 1, self.win_size)).detach()

            if u ==0:
                prior_total = (torch.mean(my_kl_loss(prior_p, series[u].detach(), self.loss_bias)) 
                            + torch.mean(my_kl_loss(series[u].detach(), prior_p, self.loss_bias)))          
                series_total = (torch.mean(my_kl_loss(series[u], series_p, self.loss_bias))
                            + torch.mean(my_kl_loss(series_p, series[u], self.loss_bias)))
            else:
                prior_total += (torch.mean(my_kl_loss(prior_p, series[u].detach(), self.loss_bias)) 
                                + torch.mean(my_kl_loss(series[u].detach(), prior_p, self.loss_bias)))              
                series_total += (torch.mean(my_kl_loss(series[u], series_p, self.loss_bias))
                                + torch.mean(my_kl_loss(series_p, series[u], self.loss_bias)))
                              
        series_loss = series_total / len(prior)
        prior_loss = prior_total  / len(prior)

        rec_loss = self.criterion(output, input)
        return series_loss, prior_loss, rec_loss

    def test(self):
        '''test the model with single dataset'''
        model_path = os.path.join(str(self.model_save_path), str(self.dataset) + self.model_save_file)
        if not os.path.exists(model_path):
            print("model save error!")
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        loss_magnification = 50

        criterion = nn.MSELoss(reduce=False)

        #find the threshold, evaluation
        test_labels = []
        attens_score = []
        for i, (input_data, labels) in enumerate(self.thre_loader):
            input = input_data.float().to(self.device)
            output, series, prior, _ = self.model(input)

            for u,item in enumerate(prior):
                series_p = (prior[u] / torch.unsqueeze(torch.sum(prior[u], dim=-1), dim=-1).repeat(1, 1, 1, self.win_size)).detach()
                prior_p = prior[u] / torch.unsqueeze(torch.sum(prior[u], dim=-1), dim=-1).repeat(1, 1, 1, self.win_size)

                if u == 0:
                    series_loss = my_kl_loss(series[u], series_p, self.loss_bias) * loss_magnification
                    prior_loss = my_kl_loss(prior_p, series[u].detach(), self.loss_bias) * loss_magnification
                elif u > 0:
                    series_loss += my_kl_loss(series[u], series_p, self.loss_bias) * loss_magnification
                    prior_loss += my_kl_loss(prior_p, series[u].detach(), self.loss_bias) * loss_magnification
                    
            cri = torch.softmax((-series_loss - prior_loss), dim=-1) * torch.mean(criterion(input, output), dim=-1)
            cri = cri.detach().cpu().numpy()
            attens_score.append(cri)
            test_labels.append(labels)

        attens_score = np.concatenate(attens_score, axis=0).reshape(-1)
        test_score = np.array(attens_score)
        total_score = np.concatenate([train_score, test_score], axis = 0)
        thresh = np.percentile(total_score, 100 - self.anormly_ratio)
        print("Threshold :", thresh)

        test_labels = np.concatenate(test_labels, axis=0).reshape(-1)
        test_labels = np.array(test_labels)

        pred = (test_energy > thresh).astype(int)
        gt = test_labels.astype(int)
        
        #detection adjustment
        #define delay_time=time1(when anomaly status was dectected) - time2(true time when anomaly status happened)
        delay_times = []
        
        for i in range(len(gt)-10):
            for j in range(11):
                if gt[i] == 1 and pred[i+j] == 1:
                    pred[i] = 1
                    delay_times.append(j)

        if len(delay_times) ==0:
            delay_time=0
        else:
            delay_time = np.mean(delay_times)

        pred = np.array(pred)
        gt = np.array(gt)
        
        accuracy = accuracy_score(gt, pred)
        print("Accuracy : {:0.4f}".format(accuracy))
        
        return accuracy, delay_time, thresh
