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
Initial atuned config parameters.
"""

import os
from configparser import ConfigParser
from analysis.default_config import LOCAL_ADDRS, REST_CERT_PATH, ENGINE_CERT_PATH, GRPC_CERT_PATH
from analysis.default_config import get_or_default, get_or_default_bool


class AtunedConfig:
    """initial atuned config parameters"""

    protocol = ''
    address = None
    connect = None
    port = None
    sample_num = ''
    interval = ''
    grpc_tls = False
    grpc_ca_file = ''
    grpc_server_cert = ''
    grpc_server_key = ''
    rest_host = ''
    rest_port = ''
    rest_tls = False
    rest_ca_file = ''
    rest_server_cert = ''
    rest_server_key = ''
    engine_host = ''
    engine_port = ''
    engine_tls = False
    engine_ca_file = ''
    engine_client_cert = ''
    engine_client_key = ''
    level = ''
    module = ''
    disk = ''
    network = ''
    user = ''
    noise = ''
    sel_feature = ''

    @staticmethod
    def initial_params(filename):
        """initial all params"""
        if not os.path.exists(filename):
            return False
        config = ConfigParser()
        config.read(filename)
        AtunedConfig.protocol = get_or_default(config, 'server', 'protocol', 'unix')
        AtunedConfig.address = get_or_default(config, 'server', 'address', LOCAL_ADDRS)
        AtunedConfig.connect = get_or_default(config, 'server', 'connect', None)
        AtunedConfig.port = get_or_default(config, 'server', 'port', None)
        AtunedConfig.grpc_tls = get_or_default_bool(config, 'server', 'grpc_tls', False)
        if AtunedConfig.grpc_tls:
            AtunedConfig.grpc_ca_file = get_or_default(config, 'server', 'tlsservercafile',
                                                       GRPC_CERT_PATH + 'ca.crt')
            AtunedConfig.grpc_server_cert = get_or_default(config, 'server', 'tlsservercertfile',
                                                           GRPC_CERT_PATH + 'server.crt')
            AtunedConfig.grpc_server_key = get_or_default(config, 'server', 'tlsserverkeyfile',
                                                          GRPC_CERT_PATH + 'server.key')
        AtunedConfig.sample_num = get_or_default(config, 'server', 'sample_num', '20')
        AtunedConfig.interval = get_or_default(config, 'server', 'interval', '5')
        AtunedConfig.rest_host = get_or_default(config, 'server', 'rest_host', 'localhost')
        AtunedConfig.rest_port = get_or_default(config, 'server', 'rest_port', '8383')
        AtunedConfig.rest_tls = get_or_default_bool(config, 'server', 'rest_tls', False)
        if AtunedConfig.rest_tls:
            AtunedConfig.rest_ca_file = get_or_default(config, 'server', 'tlsrestcacertfile',
                                                       REST_CERT_PATH + 'ca.crt')
            AtunedConfig.rest_server_cert = get_or_default(config, 'server',
                                                           'tlsrestservercertfile',
                                                           REST_CERT_PATH + 'server.crt')
            AtunedConfig.rest_server_key = get_or_default(config, 'server', 'tlsrestserverkeyfile',
                                                          REST_CERT_PATH + 'server.key')
        AtunedConfig.engine_host = get_or_default(config, 'server', 'engine_host', 'localhost')
        AtunedConfig.engine_port = get_or_default(config, 'server', 'engine_port', '3838')
        AtunedConfig.engine_tls = get_or_default_bool(config, 'server', 'engine_tls', False)
        if AtunedConfig.engine_tls:
            AtunedConfig.engine_ca_file = get_or_default(config, 'server', 'tlsenginecacertfile',
                                                         ENGINE_CERT_PATH + 'ca.crt')
            AtunedConfig.engine_client_cert = get_or_default(config, 'server',
                                                             'tlsengineclientcertfile',
                                                             ENGINE_CERT_PATH + 'client.crt')
            AtunedConfig.engine_client_key = get_or_default(config, 'server',
                                                            'tlsengineclientkeyfile',
                                                            ENGINE_CERT_PATH + 'client.key')
        AtunedConfig.level = get_or_default(config, 'log', 'level', 'info')
        AtunedConfig.module = get_or_default(config, 'monitor', 'module', 'mem_topo, cpu_topo')
        AtunedConfig.disk = get_or_default(config, 'system', 'disk', 'sda')
        AtunedConfig.network = get_or_default(config, 'system', 'network', 'enp5s0')
        AtunedConfig.user = get_or_default(config, 'system', 'user', 'root')
        AtunedConfig.noise = get_or_default(config, 'tuning', 'noise', '0.000000001')
        AtunedConfig.sel_feature = get_or_default_bool(config, 'tuning', 'sel_feature', False)
        return True
