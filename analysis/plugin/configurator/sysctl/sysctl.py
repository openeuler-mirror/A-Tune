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
The sub class of the Configurator, used to change the /proc/sys/* config.
"""

import subprocess
import re

from ..common import Configurator


class Sysctl(Configurator):
    """To change the /proc/sys/* config"""
    _module = "SYSCTL"
    _submod = "SYSCTL"

    def __init__(self, user=None):
        Configurator.__init__(self, user)
        self.__cmd = "sysctl"

    def _get(self, key, _):
        with open('/dev/null', 'w') as no_print:
            output = subprocess.check_output("{cmd} -n {key}".format(
                cmd=self.__cmd, key=key).split(), stderr=no_print)
        return output.decode()

    def _set(self, key, value):
        with open('/dev/null', 'w') as no_print:
            return subprocess.call(
                [self.__cmd, "-w", "{key}={value}".format(key=key, value=value)],
                shell=False, stdout=no_print, stderr=no_print)

    @staticmethod
    def check(config1, config2):
        """substring"""
        config1 = re.sub(r"\s{1,}", " ", config1)
        config2 = re.sub(r"\s{1,}", " ", config2)
        return config1 == config2
