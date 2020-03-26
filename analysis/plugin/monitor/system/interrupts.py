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
The sub class of the monitor, used to collect the system device interrupts.
"""
import getopt
import re
import subprocess
from ..common import Monitor


class SysInterrupts(Monitor):
    """To collect the system device interrupts"""
    _module = "SYS"
    _purpose = "INTERRUPTS"
    _option = '{print$1$NF}'
    _path = "/proc/interrupts"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.decode.__func__.__doc__ = Monitor.decode.__doc__ % "--nic=x"
        self.__cmd = "awk"

    def _get(self, _):
        output = subprocess.check_output("{cmd} {opt} {path}".format(
            cmd=self.__cmd, opt=self._option, path=self._path).split())
        return output.decode()

    def decode(self, info, para):
        """
        decode collected CPU interrupts info.

        :param info: The collected info string
        :param para: The option for decode,
                [%s]:
                "--nic=" to select which nic
        :returns info: decoded info
        """
        if para is None:
            pattern = re.compile(r"^(\d*):.*", re.MULTILINE)
            interrupts = pattern.findall(info)
            return " ".join(interrupts)

        nic = ""
        opts, _ = getopt.getopt(para.split(), None, ['nic='])
        for opt, val in opts:
            if opt in '--nic':
                nic = val
                break

        pattern = re.compile(r"^(\d*):{}$".format(nic.strip()), re.MULTILINE)
        interrupts = pattern.findall(info)
        return " ".join(interrupts).strip()
