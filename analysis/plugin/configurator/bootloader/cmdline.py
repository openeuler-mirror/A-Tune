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
The sub class of the Configurator, used to collect the cmdline info.
"""
import sys
from configurator.common import *
from bootutils import Utils


class Cmdline(Configurator):
    """To collect the cmdline info"""
    _module = "BOOTLOADER"
    _submod = "CMDLINE"

    def __init__(self, user=None):
        Configurator.__init__(self, user)

    def _get(self, key):
        return Utils.get_value(key)


if __name__ == "__main__":
    sys.path.insert(0, "./../../")
    if len(sys.argv) != 2:
        print('usage: ' + sys.argv[0] + ' key[=value]')
        sys.exit(-1)
    ct = Cmdline("UT1")
    print(ct.get(ct._getcfg(sys.argv[1])[0]))
