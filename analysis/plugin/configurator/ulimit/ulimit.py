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
The sub class of the Configurator, used to change the resources limit of user.
"""

import sys
import logging
import os
import re
import random
import shutil

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from configurator.common import *

logger = logging.getLogger(__name__)


class Ulimit(Configurator):
    """To change the resources limit of user"""
    _module = "ULIMIT"
    _submod = "ULIMIT"

    def __init__(self, user=None):
        Configurator.__init__(self, user)
        self.__cfg_file = "/etc/security/limits.conf"

    def _set(self, key, value):
        f = open(
            self.__cfg_file,
            mode='r+',
            buffering=-1,
            encoding=None,
            errors=None,
            newline=None,
            closefd=True)
        info = f.read()
        keyword = key.split(".")
        pattern = re.compile(
            "^\s*?(?!#)" +
            keyword[0] +
            "\s+?" +
            keyword[1] +
            "\s+?" +
            keyword[2] +
            "\s+(\w+)\s*?",
            re.ASCII | re.MULTILINE)
        searchObj = pattern.search(info)
        if searchObj is not None:
            offset = searchObj.span(1)
            file_modify(f, offset[0], offset[1] - 1, value)
        else:
            file_modify(f, len(info), -1, "\n{domain}\t{type}\t{item}\t{value}".format(
                domain=keyword[0], type=keyword[1], item=keyword[2], value=value))
        f.close()
        return 0

    def _get(self, key):
        with open(self.__cfg_file, 'r') as f:
            info = f.read()
        keyword = key.split(".")
        pattern = re.compile(
            "^\s*?(?!#)" +
            keyword[0] +
            "\s+?" +
            keyword[1] +
            "\s+?" +
            keyword[2] +
            "\s+(\w+)\s*?",
            re.ASCII | re.MULTILINE)
        searchObj = pattern.findall(info)
        if len(searchObj) == 0:
            err = GetConfigError("Fail to find {} config".format(key))
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err
        return searchObj[-1]

    def _backup(self, key, rollback_info):
        name = os.path.basename(self.__cfg_file)
        bak_file = "{path}/{file}{ver}".format(path=rollback_info, file=name,
                                               ver=random.random())
        shutil.copy(self.__cfg_file, bak_file)
        return "CPI_ROLLBACK_INFO = {}".format(bak_file)

    def _resume(self, key, value):
        if key != "CPI_ROLLBACK_INFO":
            err = ValueError("unsupported resume type: {}".format(key))
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err
        shutil.copy(value, self.__cfg_file)
        return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: ' + sys.argv[0] + ' key=value')
        sys.exit(-1)
    ct = Ulimit("UT")
    print(ct.set(sys.argv[1]))
    print(ct.get(ct._getcfg(sys.argv[1])[0]))
