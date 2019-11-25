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
Restful api for training, in order to provide the method of post.
"""

from flask import abort
from flask_restful import Resource

from optimizer.workload_characterization import WorkloadCharacterization
from resources.parser import train_post_parser
import logging

logger = logging.getLogger(__name__)


class Training(Resource):
    def post(self):
        args = train_post_parser.parse_args()
        logger.info(args)

        model_path = args.get("modelpath")
        output_path = args.get("outputpath")
        data_path = args.get("datapath")

        charaterization = WorkloadCharacterization(model_path)
        try:
            charaterization.retrain(data_path, output_path)
        except Exception as err:
            logger.error(err)
            abort(500)

        return {}, 200
