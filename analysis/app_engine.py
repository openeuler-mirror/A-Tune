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
# Create: 2020-07-17

"""
Engine application implementation.
"""

import os
import sys

from app import App

sys.path.insert(0, os.path.dirname(__file__) + "/../")
from analysis.engine import optimizer, classification, train, transfer, detect


class AppEngine(App):
    """app engine"""

    def add_resource(self):
        """flask app add resource"""
        self.api.add_resource(optimizer.Optimizer, '/v1/optimizer',
                              '/v1/optimizer/<string:task_id>')
        self.api.add_resource(classification.Classification, '/v1/classification',
                              '/v1/classification')
        self.api.add_resource(train.Training, '/v1/training', '/v1/training')
        self.api.add_resource(transfer.Transfer, '/v1/transfer', '/transfer')
        self.api.add_resource(detect.Detecting, '/v1/detecting', '/v1/detecting')


def main(filename):
    """app main function"""
    app_engine = AppEngine()
    app_engine.startup_app(filename, "engine_host", "engine_port", "engine_tls",
                           "tlsengineservercertfile", "tlsengineserverkeyfile",
                           "tlsenginecacertfile")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(-1)
    main(sys.argv[1])
