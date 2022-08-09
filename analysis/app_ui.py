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
# Create: 2022-6-25

"""
Ui application implementation.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__) + "/../")
from analysis.app import App
from analysis.ui.config import UiConfig
from analysis.ui.database import ui_tuning, ui_analysis, ui_user
from analysis.ui import offline


class AppUI(App):
    """app ui"""

    def add_resource(self):
        """flask app add resource"""
        self.api.add_resource(ui_tuning.UiTuning, '/v1/UI/tuning/<string:cmd>')
        self.api.add_resource(ui_analysis.UiAnalysis, '/v1/UI/analysis/<string:cmd>')
        self.api.add_resource(ui_user.UiUser, '/v1/UI/user/<string:cmd>')
        self.api.add_resource(offline.OfflineTunning, '/v2/UI/offline/<string:cmd>')


def main(filename):
    """app main function"""
    if not UiConfig.initial_params(filename):
        return
    app_ui = AppUI()
    app_ui.startup_app(UiConfig.ui_host, UiConfig.ui_port,
                           UiConfig.ui_tls,
                           UiConfig.ui_server_cert, UiConfig.ui_server_key,
                           UiConfig.ui_ca_file, UiConfig.level)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(-1)
    main(sys.argv[1])
