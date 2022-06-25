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

from analysis.engine.utils import utils
from analysis.engine.parser import TRANSFER_PUT_PARSER
from analysis.engine.config import EngineConfig
from analysis.default_config import ANALYSIS_DATA_PATH

LOGGER = logging.getLogger(__name__)


class Transfer(Resource):
    """restful api for transfer"""
    file_path = "/etc/atuned/"

    def post(self):
        """provide the method of post"""
        current_app.logger.info(request.files)
        save_path = request.form.get("savepath")
        file_obj = request.files.get("file")
        service = request.form.get("service")

        if service == "classification":
            os.makedirs(ANALYSIS_DATA_PATH, exist_ok=True)
            file_name = ANALYSIS_DATA_PATH + save_path.split(self.file_path + service)[1][1:]
            current_app.logger.info(file_name)
            file_obj.save(file_name)
            return file_name, 200

        file_obj.save(save_path)
        target_path = self.file_path + service
        res = utils.extract_file(save_path, target_path)
        os.remove(save_path)
        return res, 200

    @staticmethod
    def put():
        """provide the method of put"""
        if not EngineConfig.db_enable:
            return -1, 200

        from analysis.ui.database import trigger_analysis
        args = TRANSFER_PUT_PARSER.parse_args()
        LOGGER.info(args)

        curr_id = args['collect_id']
        client_ip = request.remote_addr
        if curr_id == -1:
            curr_id = trigger_analysis.add_new_collection(client_ip)
        if curr_id != -1:
            types = args['type']
            status = args['status']
            workload = args['workload_type']

            if types == 'csv' and status == 'running':
                trigger_analysis.add_collection_data(curr_id, client_ip, args['collect_data'])
            elif types == 'csv' and status == 'finished':
                trigger_analysis.change_collection_status(curr_id, client_ip, status, types)
                trigger_analysis.change_collection_info(curr_id, workload)
            elif types == 'log' and status == 'running':
                trigger_analysis.add_analysis_log(curr_id, args['collect_data'])
            else:
                trigger_analysis.change_collection_status(curr_id, client_ip, status, types)
                trigger_analysis.change_collection_info(curr_id, workload)
        return curr_id, 200
