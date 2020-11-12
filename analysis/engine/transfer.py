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
            file_name = "/var/atune_data/analysis/"
            if not os.path.exists(file_name):
                os.makedirs(file_name)
            file_name += save_path.split(self.file_path + service)[1]
            current_app.logger.info(file_name)
            current_app.logger.info(request.remote_addr)
            file_obj.save(file_name)
            return file_name, 200

        file_obj.save(save_path)
        target_path = self.file_path + service
        res = utils.extract_file(save_path, target_path)
        os.remove(save_path)
        return res, 200
