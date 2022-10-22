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


import numpy as np
import pandas as pd
import os
import json

class Processor(object):
    '''preprocess data'''
    DEFAULTS = {}

    def __init__(self, config):
        self.__dict__.update(Processor.DEFAULTS, **config)
        
    def get_namelist(self,path):
        '''get data infomation : kpis, datasets, dates, df_time'''
        dates = os.listdir(path)
        kpi_file_names = os.listdir(os.path.join(path, dates[0]))
        kpis = []
        for i in kpi_file_names:
            kpis.append(i)
    
        timestamps = []
        for i in range(np.size(dates)):
            data_df = pd.read_csv(os.path.join(path, dates[i], kpi_file_names[0]))
            timestamp = list(data_df[self.col_timestamp].drop_duplicates())
            timestamps.extend(timestamp)
            
        df_time = pd.DataFrame(data = timestamps,columns=[self.col_timestamp])
        df_time = df_time.sort_values(by = self.col_timestamp)
        df_time = df_time.reset_index(drop = True)
        datasets = list(data_df[self.col_service].drop_duplicates())
        return kpis, datasets, dates, df_time
    
    def fill_data(self, df, all_timestamp):
        '''fill or remove part of the raw data'''

        #df: data that is missed or duplicate and needed to process. all_timestamp : whole timestamp of data
        time_size = np.shape(all_timestamp)[0]
        df.drop_duplicates(self.col_timestamp,inplace = True)
        
        if df.shape[0] == time_size:
            return df
            
        elif df.shape[0] < time_size:
        
            #calculate the feature mean
            fill_value = df.iloc[:,1].mean()
    
            #create new dataframe for the lack data
            df_fill = pd.DataFrame(columns = [self.col_timestamp,self.col_value])
    
            #calculate the lack timestamp and related feature
            df_fill[self.col_timestamp] = list(set(all_timestamp[self.col_timestamp]) - set(df[self.col_timestamp]))
    
            #replace lack feature with the mean of feature
            df_fill.iloc[:, 1].fillna(fill_value, inplace = True)
    
            #add the dataframe to initial dataframe
            df = pd.concat([df, df_fill], ignore_index = True)
            df.sort_values(by = self.col_timestamp, inplace = True)
            return df
            
        elif df.shape[0] > time_size :
            #duplicate features with same timestamp,so drop them
            df.drop_duplicates(self.col_timestamp, inplace = True)
            df.sort_values(by = self.col_timestamp, inplace = True)
            return df
        return None
    
    def process_test_data(self):
        '''process test data of the filled data'''
        kpis, datasets, dates, df_timestamp = self.get_namelist(self.raw_test_path)
        service_df = {}
        for i in range(np.size(datasets)):
            service_df[datasets[i]] = df_timestamp
        
        for kpi in kpis:
            data_df = pd.DataFrame()
            for i in range(np.size(dates)):
                data_df_tmp = pd.read_csv(os.path.join(self.raw_test_path, dates[i], kpi))
                data_df = pd.concat([data_df, data_df_tmp])

            for dataset in datasets: 
                df_temp = data_df[data_df[self.col_service] == dataset]
                df_temp = df_temp.sort_values(by = self.col_timestamp)
                df_temp = self.fill_data(df_temp.loc[:, [self.col_timestamp, self.col_value]],  df_timestamp)
                service_df[dataset][kpi[4:-4]] = list(df_temp[self.col_value])

        for i in range(np.size(datasets)):
            service_df[datasets[i]].to_csv(os.path.join(self.test_path, datasets[i][7:] + self.save_type), index = 0)
    
    def process_train_data(self):
        '''process train data of the filled data'''
        kpis, datasets, dates, df_timestamp = self.get_namelist(self.raw_train_path)
        service_df = {}
        for i in range(np.size(datasets)):
            service_df[datasets[i]] = df_timestamp
    
        for kpi in kpis:
            data_df = pd.DataFrame()
            for i in range(np.size(dates)):
                data_df_tmp = pd.read_csv(os.path.join(self.raw_train_path, dates[i], kpi))
                data_df = pd.concat([data_df, data_df_tmp])

            for dataset in datasets: 
                df_temp = data_df[data_df[self.col_service] == dataset]
                df_temp = df_temp.sort_values(by = self.col_timestamp)
                df_temp = self.fill_data(df_temp.loc[:, [self.col_timestamp, self.col_value]], df_timestamp)
                service_df[dataset][kpi[4:-4]] = list(df_temp[self.col_value])

        for i in range(np.size(datasets)):
            service_df[datasets[i]].to_csv(os.path.join(self.train_path, datasets[i][7:] + self.save_type), index = 0)

    def df_time_process(self, times):
        '''process timestamp of the label(anomaly_data)'''
        df_anomaly_time = pd.DataFrame(columns = [self.col_timestamp, self.col_label])
        anomaly_time = []
        for time in times:
            period = int((time - self.label_start_time)/60)
            time = self.label_start_time + (period + 1)*60
            anomaly_time.append(time)
        df_anomaly_time[self.col_timestamp] = list(set(anomaly_time))
        df_anomaly_time.iloc[:, 1].fillna(1, inplace = True)
        return df_anomaly_time

    def process_label(self):
        '''process label data of the filled data'''
        kpis, datasets, dates, df_timestamp = self.get_namelist(self.raw_test_path) 
        files = os.listdir(self.raw_label_path)
        df_label_raw = pd.DataFrame(columns = [self.col_timestamp, self.col_service])
        
        for file_tmp in files:
            with open(os.path.join(self.raw_label_path, file_tmp), 'r', encoding = 'utf8') as fp:
                json_data = json.load(fp)
                df_temp = pd.DataFrame({self.col_timestamp:json_data[self.col_timestamp], self.col_service:json_data[self.col_service], self.col_level:json_data[self.col_level]})
                # delete anomaly caused by node
                df_temp = df_temp.drop(df_temp[df_temp[self.col_level].str.contains(self.col_node)].index)
                df_label_raw = df_label_raw.append(df_temp.iloc[:,0:2], ignore_index = True)

        for dataset in datasets:
            anomaly_time = []
            for index, row in df_label_raw.iterrows():
                if row[self.col_service] in dataset:
                    anomaly_time.append(row[self.col_timestamp])

            df_anomaly_time = self.df_time_process(anomaly_time)
            df_temp = pd.DataFrame(columns = [self.col_timestamp, self.col_label])
            df_temp[self.col_timestamp] = [x for x in list(df_timestamp[self.col_timestamp]) if x not in list(df_anomaly_time[self.col_timestamp])]
            df_temp[self.col_label] = 0
            df_label = pd.concat([df_temp, df_anomaly_time], ignore_index=True)
            df_label.sort_values(by = self.col_timestamp, inplace=True)
            df_label.to_csv(os.path.join(self.label_path, dataset[7:] + self.save_type), index = 0)
   
