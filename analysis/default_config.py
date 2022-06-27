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
Default path config.
"""

LOCAL_ADDRS = '/var/run/atuned/atuned.sock'
REST_CERT_PATH = '/etc/atuned/rest_certs/'
ENGINE_CERT_PATH = '/etc/atuned/engine_certs/'
UI_CERT_PATH = '/etc/atuned/ui_certs/'
GRPC_CERT_PATH = '/etc/atuned/grpc_certs'
ANALYSIS_DATA_PATH = '/var/atune_data/analysis/'
TUNING_DATA_PATH = '/var/atune_data/tuning/'
TUNING_DATA_DIRS = ['running', 'finished', 'error']


def get_or_default(config, section, key, value):
    """get or default param"""
    if config.has_option(section, key):
        return config.get(section, key)
    return value


def get_or_default_bool(config, section, key, value):
    """get or default boolean param"""
    if config.has_option(section, key):
        return config.get(section, key).lower() == 'true'
    return value
