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
The sub class of the Configurator, used to change the bios config.
"""

import sys
import logging
import subprocess

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from configurator.common import *

logger = logging.getLogger(__name__)


class Bios(Configurator):
    """To change the bios config"""
    _module = "BIOS"
    _submod = "BIOS"

    def __init__(self, user=None):
        Configurator.__init__(self, user)

    def _set(self, key, value):
        raise NeedConfigWarning(
            "Please change the BIOS configuration {key} to {val}.".format(
                key=key, val=value))

    def _get(self, key):
        if key.lower() == "version":
            output = subprocess.check_output(
                "dmidecode -t bios | grep -Po '(?<=Version:)(.*)' | sed 's/^ *//g' | sed 's/ *$//g'",
                shell=True)
            return output.decode()
        elif key.lower() == "hpre_support":
            ret = subprocess.call(
                "lspci | grep HPRE",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            if ret == 0:
                return "yes"
            else:
                return "no"
        else:
            err = NotImplementedError(
                "{} can not get {}".format(
                    self._module, key))
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err

    def _backup(self, key, rollback_info):
        return ""

    def _resume(self, key, value):
        return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: ' + sys.argv[0] + ' key=value')
        sys.exit(-1)
    ct = Bios("UT")
    print(ct.get(ct._getcfg(sys.argv[1])[0]))
