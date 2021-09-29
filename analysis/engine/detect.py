#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2020-09-30

"""
Restful api for detecting, in order to provide the method of post.
"""
import os
import logging
from glob import glob
from flask import abort
from flask_restful import Resource

from analysis.optimizer.difference_detect import WorkloadStatistic, DetectItem
from analysis.engine.parser import DETECT_POST_PARSER

LOGGER = logging.getLogger(__name__)


class Detecting(Resource):
    """provide the method of get for detecting"""
    app_name = "appname"
    detect_path = "detectpath"
    folder_path = "/var/atune_data/analysis/"

    def get(self):
        """
        :returns result, 200 : detect result, status code
        """
        args = DETECT_POST_PARSER.parse_args()
        LOGGER.info(args)

        app_name = args.get(self.app_name)
        detect_path = args.get(self.detect_path)
        if detect_path == "" or detect_path is None:
            globpath = self.folder_path + '*.csv'
            paths = glob(globpath)
            detect_path = max(paths, key=os.path.getctime)
        else:
            detect_path = self.folder_path + detect_path + '.csv'
        data_path = "/usr/libexec/atuned/analysis/dataset"
        data_path = os.path.join(data_path, "*.csv")
        statis = WorkloadStatistic()
        statis.statistic(data_path)
        detect = DetectItem(statis.statistics, statis.data_features)
        try:
            result = detect.detection(detect_path, app_name)
        except Exception as err:
            LOGGER.error(err)
            abort(500)

        return result, 200, [('Access-Control-Allow-Origin', '*')]
