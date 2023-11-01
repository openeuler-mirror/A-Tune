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
Restful api for training, in order to provide the method of post.
"""
import os
import logging
import shutil
from flask import abort
from flask_restful import Resource

from analysis.optimizer.workload_characterization import WorkloadCharacterization
from analysis.engine.parser import TRAIN_POST_PARSER
from analysis.default_config import TRAINING_MODEL_PATH

LOGGER = logging.getLogger(__name__)


class Training(Resource):
    """provide the method of post for training"""
    model_path = "modelpath"
    model_name = "modelname"
    data_path = "datapath"

    def post(self):
        """
        characterization retrain
        """
        args = TRAIN_POST_PARSER.parse_args()
        LOGGER.info(args)

        model_path = args.get(self.model_path)
        model_name = args.get(self.model_name)
        data_path = args.get(self.data_path)

        valid, err = valid_model_name(model_name)
        if not valid:
            return "Illegal model name provide: {}".format(err), 400

        characterization = WorkloadCharacterization(model_path)
        output_path = TRAINING_MODEL_PATH + model_name
        if os.path.exists(output_path):
            return "File already exists!", 400
        try:
            characterization.retrain(data_path, output_path)
        except Exception as err:
            LOGGER.error(err)
            abort(500)

        return {}, 200


def valid_model_name(name):
    file_name, file_ext = os.path.splitext(name)
    
    if file_ext != ".m":
        return False, "the ext of model name should be .m"

    if file_name in ['scaler', 'aencoder', 'tencoder', 'default_clf', 'total_clf', 'throughput_performance_clf']:
        return False, "model name cannot be set as default_clf/scaler/aencoder/tencoder/throughput_performance_clf/total_clf"

    for ind, char in enumerate(file_name):
        if 'a' <= char <= 'z':
            continue
        if 'A' <= char <= 'Z':
            continue
        if '0' <= char <= '9':
            continue
        if ind != 0 and ind != len(file_name) - 1 and char == '_':
            continue
        return False, "model name cannot contains special character"

    return True, None

