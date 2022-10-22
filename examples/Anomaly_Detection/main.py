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


import os
import sys
import argparse
import yaml
import json
from torch.backends import cudnn
from data_process import Processor

parser = argparse.ArgumentParser()
parser.add_argument('mode', type=str)
parser.add_argument('config_path', type=str)
parser.add_argument('model_path', type=str)
args = parser.parse_args()

sys.path.append(args.model_path)
from detection import Detection


if __name__ == "__main__":
    
    config_file = open(args.config_path, 'r', encoding="utf-8")
    config = yaml.safe_load(config_file) 
    cudnn.benchmark = True
    
    if args.mode == 'data_process':
        processor = Processor(config['data_process'])
        processor.process_train_data()
        processor.process_test_data()
        processor.process_label()
        print('Data is processed successfully')

    elif args.mode == 'train':
        if (not os.path.exists(config['detection']['model_save_path'])):
            os.mkdir(config['detection']['model_save_path'])  
            
        detection = Detection(config['detection'])
        detection.detect("train")

    elif args.mode == 'test':
        detection = Detection(config['detection'])
        detection.detect("test")