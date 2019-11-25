#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v1.
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
# Create: 2019-10-29

"""
The sub class of the Configurator, used to change the system service config.
"""
import os
import sys
import logging
import subprocess

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from configurator.common import *

logger = logging.getLogger(__name__)


class Systemctl(Configurator):
    """To change the system service config"""
    _module = "SYSTEMCTL"
    _submod = "SYSTEMCTL"
    _option = "is-active"
    _path = "/usr/lib/systemd/system/"

    def __init__(self, user=None):
        Configurator.__init__(self, user)
        self.__cmd = "systemctl"

    def _get(self, service):
        with open('/dev/null', 'w') as no_print:
            output = subprocess.check_output(
                "{cmd} {opt} {service}; exit 0".format(
                    cmd=self.__cmd,
                    opt=self._option,
                    service=service),
                stderr=no_print,
                shell=True)
        return output.decode().replace('\n', ' ').strip()

    def _set(self, service, oper):
        if not os.path.exists(self._path + service + ".service"):
            return 0
        status = self._get(service)
        if status == "active" and oper == "start" or status == "inactive" and oper == "stop":
            return 0
        with open('/dev/null', 'w') as no_print:
            return subprocess.call("{cmd} {oper} {service}".format(
                cmd=self.__cmd, service=service, oper=oper).split(),
                stdout=no_print, stderr=no_print)

    def _check(self, config1, config2):
        return True

    def _backup(self, key, rollback_info):
        val = self._get(key)
        if val == "active" or val == "activating":
            val = "start"
        else:
            val = "stop"
        return "{} = {}".format(key, val)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: ' + sys.argv[0] + ' service=oper')
        sys.exit(-1)
    ct = Systemctl("UT")
    print(ct.set(sys.argv[1]))
    print(ct.get(ct._getcfg(sys.argv[1])[0]))
