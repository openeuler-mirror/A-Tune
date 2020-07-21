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

LOGGER = logging.getLogger(__name__)


class Training(Resource):
    """provide the method of post for training"""
    model_path = "modelpath"
    output_path = "outputpath"
    data_path = "datapath"

    def post(self):
        """
        characterization retrain
        """
        args = TRAIN_POST_PARSER.parse_args()
        LOGGER.info(args)

        model_path = args.get(self.model_path)
        output_path = args.get(self.output_path)
        data_path = args.get(self.data_path)

        characterization = WorkloadCharacterization(model_path)
        try:
            characterization.retrain(data_path, output_path)
        except Exception as err:
            LOGGER.error(err)
            abort(500)

        if os.path.isdir(data_path):
            shutil.rmtree(data_path)
        else:
            os.remove(data_path)
        return {}, 200
