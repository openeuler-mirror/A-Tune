#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-10-29

"""
The sub class of the monitor, used to collect the file handles util info.
"""
import inspect
import logging
import getopt
import re
from ..common import Monitor

LOGGER = logging.getLogger(__name__)


class SysFdUtil(Monitor):
    """To collect the file handles util info"""
    _module = "SYS"
    _purpose = "FDUTIL"
    _option = "/proc/sys/fs/file-nr"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.decode.__func__.__doc__ = Monitor.decode.__doc__ % (
            "--fields=allocated/pending/maximum/fd-util")

    def _get(self, _):
        with open(self._option, 'r') as file:
            fdinfo = file.read()
        return fdinfo

    def decode(self, info, para):
        """
        decode the result of the operation
        :param info:  content that needs to be decoded
        :param para:  command line argument
        :returns ret:  operation result
        """
        if para is None:
            return info

        keyword = {"allocated": 0,
                   "pending": 1,
                   "maximum": 2,
                   "fd-util": "fd-util"}

        keys = []
        ret = ""

        opts, _ = getopt.getopt(para.split(), None, ['fields='])
        for opt, val in opts:
            if opt in '--fields':
                keys.append(keyword[val])
                continue

        pattern = re.compile(
            r"^(\d*)\s{1,}(\d*)\s{1,}(\d*)",
            re.ASCII | re.MULTILINE)
        search_obj = pattern.findall(info)
        if len(search_obj) == 0:
            err = LookupError("Fail to find data")
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err

        for i in keys:
            if type(i).__name__ == 'int':
                ret = ret + " " + search_obj[-1][i]
            elif i == "fd-util":
                util = int(search_obj[-1][keyword["allocated"]]) / \
                       int(search_obj[-1][keyword["maximum"]]) * 100
                ret = ret + " " + str(util)
        return ret
