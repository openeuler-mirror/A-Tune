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
The sub class of the monitor, used to collect the CPU topo.
"""

import sys
import logging
import subprocess

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from monitor.common import *

logger = logging.getLogger(__name__)


class CpuTopo(Monitor):
    """To collect the CPU topo"""
    _module = "CPU"
    _purpose = "TOPO"
    _option = "--no-io --ignore misc"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.format.__func__.__doc__ = Monitor.format.__doc__ % ("xml")
        with open('/dev/null', 'w') as no_print:
            if 0 == subprocess.call("which lstopo-no-graphics".split(),
                                    stdout=no_print, stderr=no_print):
                self.__cmd = "lstopo-no-graphics"
            elif 0 == subprocess.call("which lstopo".split(), stdout=no_print,
                                      stderr=no_print):
                self.__cmd = "lstopo"

    def _get(self, para=None):
        output = subprocess.check_output("{cmd} {opt}".format(
            cmd=self.__cmd, opt=self._option).split())
        return output.decode()

    def format(self, info, fmt):
        if (fmt == "xml"):
            o_xml = subprocess.check_output("{cmd} --of xml {opt}".format(
                                            cmd=self.__cmd, opt=self._option).split())
            return o_xml.decode()
        elif (fmt == "table"):
            o_xml = subprocess.check_output("{cmd} --of ascii {opt}".format(
                                            cmd=self.__cmd, opt=self._option).split())
            return o_xml.decode()
        else:
            return Monitor.format(self, info, fmt)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: ' + sys.argv[0] + ' fmt path')
        sys.exit(-1)
    ct = CpuTopo("UT")
    ct.report(sys.argv[1], sys.argv[2])
