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
The sub class of the monitor, used to collect the CPU isolation info.
"""
import re
import sys
import subprocess
from monitor.common import *


class CpuIsolate(Monitor):
    """To collect the CPU isolation info"""
    _module = "CPU"
    _purpose = "ISOLATION"
    _path = "/proc/cmdline"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__cmd = "cat"

    def _get(self, para=None):
        output = subprocess.check_output("{cmd} {path}".format(
            cmd=self.__cmd, path=self._path).split())
        return output.decode()

    def decode(self, info, para=None):
        """
        decode collected CPU isolation info.

        :param info: The collected info string
        :param para: The option for decode, para is None
        :returns info: decoded info
        """
        pattern = re.compile(r"isolcpus=([\d,]*)", re.MULTILINE)
        cpus = pattern.findall(info)
        return " ".join(cpus).strip()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: ' + sys.argv[0] + ' fmt path')
        sys.exit(-1)
    ct = CpuIsolate("UT")
    ct.report(sys.argv[1], sys.argv[2])
