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


cd ../../anomaly_detection

#get models
git clone https://github.com/thuml/Anomaly-Transformer

#change "-" to "_"
mv Anomaly-Transformer Anomaly_Transformer


cd ../examples/Anomaly_Detection

mkdir data/train
mkdir data/test
mkdir data/label

#data preprocess
python main.py data_process ./config.yaml ../../anomaly_detection/

#train
python main.py train ./config.yaml ../../anomaly_detection/

#test
python main.py test ./config.yaml ../../anomaly_detection/