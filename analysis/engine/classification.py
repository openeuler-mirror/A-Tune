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
Restful api for classification, in order to provide the method of post.
"""

import logging
from flask import abort
from flask import current_app
from flask_restful import Resource
from flask_restful import marshal_with_field

from analysis.optimizer.workload_characterization import WorkloadCharacterization
from analysis.engine.field import CLASSIFICATION_POST_FIELD
from analysis.engine.parser import CLASSIFICATION_POST_PARSER
from analysis.engine.utils import utils

LOGGER = logging.getLogger(__name__)


class Classification(Resource):
    """restful api for classification, in order to provide the method of post"""
    model_path = "modelpath"
    data_path = "data"
    model = "model"

    @marshal_with_field(CLASSIFICATION_POST_FIELD)
    def post(self):
        """provide the method of post"""
        args = CLASSIFICATION_POST_PARSER.parse_args()
        current_app.logger.info(args)

        model_path = args.get(self.model_path)
        data_path = args.get(self.data_path)
        model = args.get(self.model, None)
        data = utils.read_from_csv(data_path)
        if data.empty:
            abort("data may be not exist")

        classification = WorkloadCharacterization(model_path)
        resource_limit = ""
        if model is None:
            resource_limit, workload_type, percentage = classification.identify(data)
        else:
            workload_type, percentage = classification.reidentify(data, model)

        profile_name = {}
        profile_name["workload_type"] = workload_type
        profile_name["percentage"] = percentage
        profile_name["resource_limit"] = resource_limit
        return profile_name, 200
