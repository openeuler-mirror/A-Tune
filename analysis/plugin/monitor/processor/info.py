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
The sub class of the monitor, used to collect the CPU info.
"""

import subprocess
from ..common import Monitor


class CpuInfo(Monitor):
    """To collect the CPU info"""
    _module = "CPU"
    _purpose = "INFO"
    _option = "-c processor"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__cmd = "lshw"
        self.format.__func__.__doc__ = Monitor.format.__doc__ % ("xml, json")

    def _get(self, _):
        with open('/dev/null', 'w') as no_print:
            output = subprocess.check_output("{cmd} {opt}".format(
                cmd=self.__cmd, opt=self._option).split(),
                                             stderr=no_print)
        return output.decode()

    def format(self, info, fmt):
        """
        format the result of the operation
        :param info:  content that needs to be converted
        :param fmt:  converted format
        :returns output:  converted result
        """
        if fmt == "xml":
            o_xml = subprocess.check_output(
                "{cmd} -xml {opt}".format(
                    cmd=self.__cmd,
                    opt=self._option).split(),
                stderr=subprocess.DEVNULL)
            return o_xml.decode()
        if fmt == "json":
            o_json = subprocess.check_output("{cmd} -json {opt}".format(
                cmd=self.__cmd, opt=self._option).split(),
                                             stderr=subprocess.DEVNULL)
            return o_json.decode()
        return Monitor.format(self, info, fmt)
