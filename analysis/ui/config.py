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
Initial ui config parameters.
"""

import os
from configparser import ConfigParser
from analysis.default_config import UI_CERT_PATH
from analysis.default_config import get_or_default, get_or_default_bool


class UiConfig:
    """initial ui config parameters"""

    ui_host = ''
    ui_port = ''
    ui_tls = False
    ui_ca_file = ''
    ui_server_cert = ''
    ui_server_key = ''
    level = ''
    db_enable = False
    database = ''
    db_host = ''
    db_port = ''
    db_name = ''
    db_user_name = ''
    db_user_passwd = ''
    db_passwd_key = ''
    db_passwd_iv = ''

    @staticmethod
    def initial_params(filename):
        """initial all params"""
        if not os.path.exists(filename):
            return False
        config = ConfigParser()
        config.read(filename)
        UiConfig.ui_host = get_or_default(config, 'server', 'ui_host', 'localhost')
        UiConfig.ui_port = get_or_default(config, 'server', 'ui_port', '3839')
        UiConfig.ui_tls = get_or_default_bool(config, 'server', 'ui_tls', False)
        if UiConfig.ui_tls:
            UiConfig.ui_ca_file = get_or_default(config, 'server',
                    'tlsuicacertfile', UI_CERT_PATH + 'ca.crt')
            UiConfig.ui_server_cert = get_or_default(config, 'server',
                    'tlsuiservercertfile', UI_CERT_PATH + 'server.crt')
            UiConfig.ui_server_key = get_or_default(config, 'server',
                    'tlsuiserverkeyfile', UI_CERT_PATH + 'server.key')
        UiConfig.level = get_or_default(config, 'log', 'level', 'info')
        UiConfig.db_enable = get_or_default_bool(config, 'database', 'db_enable', False)
        if UiConfig.db_enable:
            UiConfig.database = get_or_default(config, 'database', 'database', 'PostgreSQL')
            UiConfig.db_host = get_or_default(config, 'database', 'db_host', 'localhost')
            UiConfig.db_port = get_or_default(config, 'database', 'db_port', '5432')
            UiConfig.db_name = get_or_default(config, 'database', 'db_name', 'atune_db')
            UiConfig.db_user_name = get_or_default(config, 'database', 'db_user_name', 'admin')
            UiConfig.db_user_passwd = get_or_default(config, 'database', 'db_user_passwd', '')
            UiConfig.db_passwd_key = get_or_default(config, 'database', 'db_passwd_key', '')
            UiConfig.db_passwd_iv = get_or_default(config, 'database', 'db_passwd_iv', '')
        return True
