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
from analysis.default_config import get_or_default, get_or_default_bool, get_or_default_list


class EngineConfig:
    """initial engine config parameters"""

    engine_host = ''
    engine_port = ''
    engine_tls = False
    engine_ca_file = ''
    engine_server_cert = ''
    engine_server_key = ''
    level = ''
    log_dir = None
    db_enable = False
    database = ''
    db_host = ''
    db_port = ''
    db_name = ''
    db_user_name = ''
    db_user_passwd = ''
    db_passwd_key = ''
    db_passwd_iv = ''
    db_analysis_type = []

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
        EngineConfig.log_dir = get_or_default(config, 'log', 'level', None)
        EngineConfig.db_enable = get_or_default_bool(config, 'database', 'db_enable', False)
        if EngineConfig.db_enable:
            EngineConfig.database = get_or_default(config, 'database', 'database', 'PostgreSQL')
            EngineConfig.db_host = get_or_default(config, 'database', 'db_host', 'localhost')
            EngineConfig.db_port = get_or_default(config, 'database', 'db_port', '5432')
            EngineConfig.db_name = get_or_default(config, 'database', 'db_name', 'atune_db')
            EngineConfig.db_user_name = get_or_default(config, 'database', 'db_user_name', 'admin')
            EngineConfig.db_user_passwd = get_or_default(config, 'database', 'db_user_passwd', '')
            EngineConfig.db_passwd_key = get_or_default(config, 'database', 'db_passwd_key', '')
            EngineConfig.db_passwd_iv = get_or_default(config, 'database', 'db_passwd_iv', '')
            EngineConfig.db_analysis_type = get_or_default_list(config, 'database', 'db_analysis_type', [])
        
        # bottleneck
        # computing
        EngineConfig.cpu_stat_util = get_or_default(config, 'bottleneck', 'cpu_stat_util', '80')
        EngineConfig.cpu_stat_cutil = get_or_default(config, 'bottleneck', 'cpu_stat_cutil', '80')
        EngineConfig.perf_stat_ipc = get_or_default(config, 'bottleneck', 'perf_stat_ipc', '1')
        # memory
        EngineConfig.mem_bandwidth_total_util = get_or_default(config, 'bottleneck', 'mem_bandwidth_total_util', '70')
        EngineConfig.mem_vmstat_util_swap = get_or_default(config, 'bottleneck', 'mem_vmstat_util_swap', '70')
        EngineConfig.mem_vmstat_util_cpu = get_or_default(config, 'bottleneck', 'mem_vmstat_util_cpu', '70')
        # network
        EngineConfig.net_stat_ifutil = get_or_default(config, 'bottleneck', 'net_stat_ifutil', '70')
        EngineConfig.net_estat_errs = get_or_default(config, 'bottleneck', 'net_estat_errs', '1')
        # network I/O
        EngineConfig.net_stat_rxkbs = get_or_default(config, 'bottleneck', 'net_stat_rxkbs', '70')
        EngineConfig.net_stat_txkbs = get_or_default(config, 'bottleneck', 'net_stat_txkbs', '70')
        #disk I/OF
        EngineConfig.storage_stat_util = get_or_default(config, 'bottleneck', 'storage_stat_util', '70')
            
        return True
