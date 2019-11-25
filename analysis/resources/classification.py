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
Restful api for classification, in order to provide the method of post.
"""

from flask import abort
from flask import current_app
from flask_restful import Resource
from flask_restful import marshal_with_field

from optimizer.workload_characterization import WorkloadCharacterization
from resources.field import classification_post_field
from resources.parser import classification_post_parser
from utils import utils
import logging

logger = logging.getLogger(__name__)


class Classification(Resource):
    @marshal_with_field(classification_post_field)
    def post(self):
        args = classification_post_parser.parse_args()
        current_app.logger.info(args)

        model_path = args.get("modelpath")
        data_path = args.get("data")
        model = args.get("model", None)
        data = utils.readFromCsv(data_path)
        if not data:
            abort("data path may be not exist")

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

