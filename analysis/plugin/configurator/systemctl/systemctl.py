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
The sub class of the Configurator, used to change the system service config.
"""
import os
import subprocess
from ..common import Configurator


class Systemctl(Configurator):
    """To change the system service config"""
    _module = "SYSTEMCTL"
    _submod = "SYSTEMCTL"
    _option = "is-active"
    _path = "/usr/lib/systemd/system/"

    def __init__(self, user=None):
        Configurator.__init__(self, user)
        self.__cmd = "systemctl"

    def _get(self, key, _):
        with open('/dev/null', 'w') as no_print:
            output = subprocess.Popen(
                [self.__cmd, self._option, key],
                stdout=subprocess.PIPE,
                stderr=no_print,
                shell=False)
            out = output.communicate()
        return bytes.decode(out[0]).replace('\n', ' ').strip()

    def _set(self, key, value):
        if not os.path.exists(self._path + key + ".service"):
            return 0
        status = self._get(key, value)
        if status == "active" and value == "start" or status == "inactive" and value == "stop":
            return 0
        with open('/dev/null', 'w') as no_print:
            return subprocess.call("{cmd} {oper} {service}".format(
                cmd=self.__cmd, service=key, oper=value).split(),
                                   stdout=no_print, stderr=no_print)

    @staticmethod
    def check(_, __):
        """check"""
        return True

    def _backup(self, config, _):
        cfg = self._getcfg(config)
        val = self._get(cfg[0], cfg[1])
        if val in ("active", "activating"):
            val = "start"
        else:
            val = "stop"
        return "{} = {}".format(cfg[0], val)
