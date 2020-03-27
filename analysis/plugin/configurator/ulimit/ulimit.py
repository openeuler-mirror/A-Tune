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
The sub class of the Configurator, used to change the resources limit of user.
"""
import inspect
import logging
import os
import re
import random
import shutil
from analysis.plugin.public import GetConfigError
from ..common import Configurator, file_modify

LOGGER = logging.getLogger(__name__)


class Ulimit(Configurator):
    """To change the resources limit of user"""
    _module = "ULIMIT"
    _submod = "ULIMIT"

    def __init__(self, user=None):
        Configurator.__init__(self, user)
        self.__cfg_file = "/etc/security/limits.conf"

    def _set(self, key, value):
        with open(self.__cfg_file, mode='r+', buffering=-1, encoding=None, errors=None,
                  newline=None, closefd=True) as file:
            info = file.read()
            keyword = key.split(".")
            pattern = re.compile(
                r"^\s*?(?!#)" +
                keyword[0] +
                r"\s+?" +
                keyword[1] +
                r"\s+?" +
                keyword[2] +
                r"\s+(\w+)\s*?",
                re.ASCII | re.MULTILINE)
            search_obj = pattern.search(info)
            if search_obj is not None:
                offset = search_obj.span(1)
                file_modify(file, offset[0], offset[1] - 1, value)
            else:
                file_modify(file, len(info), -1, "\n{domain}\t{type}\t{item}\t{value}".format(
                    domain=keyword[0], type=keyword[1], item=keyword[2], value=value))
        return 0

    def _get(self, key, _):
        with open(self.__cfg_file, 'r') as file:
            info = file.read()
        keyword = key.split(".")
        pattern = re.compile(
            r"^\s*?(?!#)" +
            keyword[0] +
            r"\s+?" +
            keyword[1] +
            r"\s+?" +
            keyword[2] +
            r"\s+(\w+)\s*?",
            re.ASCII | re.MULTILINE)
        search_obj = pattern.findall(info)
        if len(search_obj) == 0:
            err = GetConfigError("Fail to find {} config".format(key))
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err
        return search_obj[-1]

    def _backup(self, _, rollback_info):
        name = os.path.basename(self.__cfg_file)
        bak_file = "{path}/{file}{ver}".format(path=rollback_info, file=name,
                                               ver=random.random())
        shutil.copy(self.__cfg_file, bak_file)
        return "CPI_ROLLBACK_INFO = {}".format(bak_file)

    def _resume(self, key, value):
        if key != "CPI_ROLLBACK_INFO":
            err = ValueError("unsupported resume type: {}".format(key))
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err
        shutil.copy(value, self.__cfg_file)
