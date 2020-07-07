#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2020-06-18

"""
The sub class of the Configurator, used to change the file config.
"""
import inspect
import logging
import os
import random
import re
import shutil

from analysis.plugin.public import GetConfigError, NeedConfigWarning
from ..common import Configurator

LOGGER = logging.getLogger(__name__)


class FileConfig(Configurator):
    """To change the file config"""
    _module = "FILE_CONFIG"
    _submod = "FILE_CONFIG"
    _cfg_files = ["/etc/profile"]
    _separator_char = "-"

    def __init__(self, user=None):
        Configurator.__init__(self, user)

    def _set(self, key, value):
        try:
            if self.get(key, value) == value:
                return 0
        except LookupError as err:
            LOGGER.debug("%s.%s: %s", self.__class__.__name__, inspect.stack()[0][3], str(err))

        with open(key, 'a') as file:
            file.write(value + "\n")

        if key in self._cfg_files:
            raise NeedConfigWarning(
                "please exec source {file} to make the configuration take effect".format(file=key))
        return 0

    def _get(self, key, value):
        if not os.path.exists(key):
            raise GetConfigError("Fail to find file {}".format(key))

        config_key = value.split("=")[0] if value.find("=") != -1 else value
        pattern = re.compile("^" + config_key + ".*", re.ASCII | re.DOTALL)
        search_obj = []
        with open(key, 'r') as file:
            for line in file:
                result = pattern.search(line)
                if result is not None:
                    search_obj.append(result.group(0).strip())

        if len(search_obj) == 0:
            raise LookupError("Fail to find {} entry in {}".format(config_key, key))

        return search_obj[-1]

    def _backup(self, config, rollback_info):
        cfg = self._getcfg(config)
        name = cfg[0].replace("/", self._separator_char)
        bak_file = "{path}/{file}{sep}{ver}".format(path=rollback_info, file=name,
                                                    sep=self._separator_char,
                                                    ver=random.random())
        shutil.copy(cfg[0], bak_file)
        return "CPI_ROLLBACK_INFO = {}".format(bak_file)

    def _resume(self, key, value):
        if key != "CPI_ROLLBACK_INFO":
            raise ValueError("unsupported resume type: {}".format(key))
        left_index = value.rfind("/")
        right_index = value.rfind(self._separator_char)
        if left_index == -1 or right_index == -1:
            return
        cfg_file = value[left_index + 1:right_index].replace(self._separator_char, "/")
        LOGGER.info("resume cfg file is %s", cfg_file)
        shutil.copy(value, cfg_file)
