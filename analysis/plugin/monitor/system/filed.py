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
The sub class of the monitor, used to collect the file handles util info.
"""

import sys
import logging
import subprocess
import getopt
import re

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from monitor.common import *

logger = logging.getLogger(__name__)


class SysFdUtil(Monitor):
    """To collect the file handles util info"""
    _module = "SYS"
    _purpose = "FDUTIL"
    _option = "/proc/sys/fs/file-nr"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.decode.__func__.__doc__ = Monitor.decode.__doc__ % (
            "--fields=allocated/pending/maximum/fd-util")

    def _get(self, para=None):
        with open(self._option, 'r') as f:
            fdinfo = f.read()
        return fdinfo

    def decode(self, info, para):
        if para is None:
            return info

        keyword = {"allocated": 0,
                    "pending": 1,
                    "maximum": 2,
                    "fd-util": "fd-util"}

        keys = []
        ret = ""

        opts, args = getopt.getopt(para.split(), None, ['fields='])
        for opt, val in opts:
            if opt in ('--fields'):
                keys.append(keyword[val])
                continue

        pattern = re.compile(
            "^(\d*)\s{1,}(\d*)\s{1,}(\d*)",
            re.ASCII | re.MULTILINE)
        searchObj = pattern.findall(info)
        if len(searchObj) == 0:
            err = LookupError("Fail to find data")
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err

        for i in keys:
            if type(i).__name__ == 'int':
                ret = ret + " " + searchObj[-1][i]
            elif i == "fd-util":
                util = int(searchObj[-1][keyword["allocated"]]) / \
                        int(searchObj[-1][keyword["maximum"]]) * 100
                ret = ret + " " + str(util)
        return ret


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: ' + sys.argv[0] + ' fmt path')
        sys.exit(-1)
    ct = SysFdUtil("UT")
    ct.report(
        sys.argv[1],
        sys.argv[2],
        ";--fields=fd-util")
