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
The sub class of the Configurator, used to change the /sys/* config.
"""

import re

from ..common import Configurator


class Sysfs(Configurator):
    """To change the /sys/* config"""
    _module = "SYSFS"
    _submod = "SYSFS"
    _option = "/sys"

    def __init__(self, user=None):
        Configurator.__init__(self, user)

    def _get(self, key, _):
        with open("{opt}/{key}".format(opt=self._option, key=key), mode='r',
                  buffering=-1, encoding=None, errors=None, newline=None, closefd=True) as file:
            ret = file.read()

        pattern = r".*\[(.*)\].*"
        search_obj = re.search(pattern, ret, re.ASCII | re.MULTILINE)
        if search_obj is not None:
            return search_obj.group(1)
        return ret

    def _set(self, key, value):
        with open("{opt}/{key}".format(opt=self._option, key=key), mode='w',
                  buffering=-1, encoding=None, errors=None, newline=None, closefd=True) as file:
            file.write(value)
        return 0

    @staticmethod
    def check(_, __):
        return True
