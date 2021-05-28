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
Rest application implementation.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__) + "/../")
from analysis.app import App
from analysis.atuned import configurator, monitor, collector, profile
from analysis.atuned.config import AtunedConfig


class AppRest(App):
    """app rest"""

    def add_resource(self):
        """flask app add resource"""
        self.api.add_resource(configurator.Configurator, '/v1/setting', '/setting')
        self.api.add_resource(monitor.Monitor, '/v1/monitor', '/monitor')
        self.api.add_resource(collector.Collector, '/v1/collector', '/collector')
        self.api.add_resource(profile.Profile, '/v1/profile', '/profile')


def main(filename):
    """app main function"""
    if not AtunedConfig.initial_params(filename):
        return
    app_engine = AppRest()
    app_engine.startup_app(AtunedConfig.rest_host, AtunedConfig.rest_port, AtunedConfig.rest_tls,
                           AtunedConfig.rest_server_cert, AtunedConfig.rest_server_key,
                           AtunedConfig.rest_ca_file, AtunedConfig.level)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(-1)
    main(sys.argv[1])
