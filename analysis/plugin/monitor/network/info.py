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
The sub class of the monitor, used to collect the nic config info.
"""

import subprocess

from ..common import Monitor


class NetInfo(Monitor):
    """To collect the nic config info"""
    _module = "NET"
    _purpose = "INFO"
    _option = ";-l;-k"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__cmd = "ethtool"

    def _get(self, para):
        opts = self._getopt()
        outputs = ""
        while True:
            try:
                output = subprocess.check_output("{cmd} {opt} {para}".format(
                    cmd=self.__cmd, opt=next(opts), para=para).split())
                outputs += output.decode()
            except StopIteration:
                return outputs
