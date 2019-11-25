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
The sub class of the Configurator, used to change the /sys/* config.
"""

import sys
import logging
import re

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from configurator.common import *

logger = logging.getLogger(__name__)


class Sysfs(Configurator):
    """To change the /sys/* config"""
    _module = "SYSFS"
    _submod = "SYSFS"
    _option = "/sys"

    def __init__(self, user=None):
        Configurator.__init__(self, user)

    def _get(self, key):
        f = open("{opt}/{key}".format(opt=self._option, key=key), mode='r',
                 buffering=-1, encoding=None, errors=None, newline=None, closefd=True)
        ret = f.read()
        f.close()

        pattern = ".*\[(.*)\].*"
        searchObj = re.search(pattern, ret, re.ASCII | re.MULTILINE)
        if searchObj is not None:
            return searchObj.group(1)
        else:
            return ret

    def _set(self, key, value):
        f = open("{opt}/{key}".format(opt=self._option, key=key), mode='w',
                 buffering=-1, encoding=None, errors=None, newline=None, closefd=True)
        f.write(value)
        f.close()
        return 0

    def _check(self, config1, config2):
        return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: ' + sys.argv[0] + ' key=value')
        sys.exit(-1)
    ct = Sysfs("UT")
    print(ct.set(sys.argv[1]))
    print(ct.get(ct._getcfg(sys.argv[1])[0]))
