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
The sub class of the monitor, used to collect the nic config info.
"""

import sys
import logging
import subprocess

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from monitor.common import *

logger = logging.getLogger(__name__)


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


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('usage: ' + sys.argv[0] + ' fmt path dev')
        sys.exit(-1)
    ct = NetInfo("UT")
    ct.report(sys.argv[1], sys.argv[2], sys.argv[3])
