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
The sub class of the monitor, used to collect the CPU topo.
"""

import subprocess
from ..common import Monitor


class CpuTopo(Monitor):
    """To collect the CPU topo"""
    _module = "CPU"
    _purpose = "TOPO"
    _option = "--no-io --ignore misc"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.format.__func__.__doc__ = Monitor.format.__doc__ % ("xml")
        with open('/dev/null', 'w') as no_print:
            if subprocess.call("which lstopo-no-graphics".split(),
                               stdout=no_print, stderr=no_print) == 0:
                self.__cmd = "lstopo-no-graphics"
            elif subprocess.call("which lstopo".split(), stdout=no_print,
                                 stderr=no_print) == 0:
                self.__cmd = "lstopo"
            else:
                self.__cmd = None

    def _get(self, _):
        output = subprocess.check_output("{cmd} {opt}".format(
            cmd=self.__cmd, opt=self._option).split())
        return output.decode()

    def format(self, info, fmt):
        """
        format the result of the operation
        :param info:  content that needs to be converted
        :param fmt:  converted format
        :returns output:  converted result
        """
        if fmt == "xml":
            o_xml = subprocess.check_output("{cmd} --of xml {opt}".format(
                cmd=self.__cmd, opt=self._option).split())
            return o_xml.decode()
        if fmt == "table":
            o_xml = subprocess.check_output("{cmd} --of ascii {opt}".format(
                cmd=self.__cmd, opt=self._option).split())
            return o_xml.decode()
        return Monitor.format(self, info, fmt)
