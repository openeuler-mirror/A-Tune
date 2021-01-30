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
# Create: 2020-12-15

"""
Initial engine config parameters.
"""

import os
from configparser import ConfigParser
from analysis.default_config import ENGINE_CERT_PATH
from analysis.default_config import get_or_default, get_or_default_bool


class EngineConfig:
    """initial engine config parameters"""

    engine_host = ''
    engine_port = ''
    engine_tls = False
    engine_ca_file = ''
    engine_server_cert = ''
    engine_server_key = ''
    level = ''
    db_enable = False
    database = ''
    db_host = ''
    db_port = ''
    db_name = ''
    user_name = ''
    user_passwd = ''
    passwd_key = ''
    passwd_iv = ''

    @staticmethod
    def initial_params(filename):
        """initial all params"""
        if not os.path.exists(filename):
            return False
        config = ConfigParser()
        config.read(filename)
        EngineConfig.engine_host = get_or_default(config, 'server', 'engine_host', 'localhost')
        EngineConfig.engine_port = get_or_default(config, 'server', 'engine_port', '3838')
        EngineConfig.engine_tls = get_or_default_bool(config, 'server', 'engine_tls', False)
        if EngineConfig.engine_tls:
            EngineConfig.engine_ca_file = get_or_default(config, 'server',
                    'tlsenginecacertfile', ENGINE_CERT_PATH + 'ca.crt')
            EngineConfig.engine_server_cert = get_or_default(config, 'server',
                    'tlsengineservercertfile', ENGINE_CERT_PATH + 'server.crt')
            EngineConfig.engine_server_key = get_or_default(config, 'server',
                    'tlsengineserverkeyfile', ENGINE_CERT_PATH + 'server.key')
        EngineConfig.level = get_or_default(config, 'log', 'level', 'info')
        EngineConfig.db_enable = get_or_default_bool(config, 'database', 'db_enable', False)
        if EngineConfig.db_enable:
            EngineConfig.database = get_or_default(config, 'database', 'database', 'PostgreSQL')
            EngineConfig.db_host = get_or_default(config, 'database', 'db_host', 'localhost')
            EngineConfig.db_port = get_or_default(config, 'database', 'db_port', '5432')
            EngineConfig.db_name = get_or_default(config, 'database', 'db_name', 'atune_db')
            EngineConfig.user_name = get_or_default(config, 'database', 'user_name', 'admin')
            EngineConfig.user_passwd = get_or_default(config, 'database', 'user_passwd', '')
            EngineConfig.passwd_key = get_or_default(config, 'database', 'passwd_key', '')
            EngineConfig.passwd_iv = get_or_default(config, 'database', 'passwd_iv', '')
        return True
