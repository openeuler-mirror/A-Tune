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
# Create: 2020-07-17

"""
Restful api for transfer, in order to transfer file.
"""

import os
import logging
from flask import current_app
from flask_restful import Resource
from flask_restful import request

from analysis.engine.utils import utils, save_data
from analysis.engine.parser import TRANSFER_PUT_PARSER
from analysis.engine.config import EngineConfig
from analysis.default_config import ANALYSIS_DATA_PATH

LOGGER = logging.getLogger(__name__)


class Transfer(Resource):
    """restful api for transfer"""
    file_path = "/etc/atuned/{service}"

    def post(self):
        """provide the method of post"""
        current_app.logger.info(request.files)
        save_path = request.form.get("savepath")
        file_obj = request.files.get("file")
        service = request.form.get("service")

        target_path = self.file_path.format(service=service)
        dir_name, _ = os.path.split(os.path.abspath(save_path))
        if not dir_name == target_path:
            return "illegal path to save file", 400

        if service == "classification":
            os.makedirs(ANALYSIS_DATA_PATH, exist_ok=True)
            file_name = ANALYSIS_DATA_PATH + save_path.split(target_path)[1][1:]
            current_app.logger.info(file_name)
            file_obj.save(file_name)
            return file_name, 200

        file_obj.save(save_path)
        res = utils.extract_file(save_path, target_path)
        os.remove(save_path)
        return res, 200

    @staticmethod
    def put():
        """provide the method of put"""
        if not EngineConfig.db_enable:
            return -1, 200

        args = TRANSFER_PUT_PARSER.parse_args()
        LOGGER.info(args)

        curr_id = args['collect_id']
        client_ip = request.remote_addr
        curr_id = save_data.save_analysis_or_collection_data(args, client_ip)
        return curr_id, 200
