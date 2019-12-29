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
The sub class of the Configurator, used to change the kernel config.
"""
import gzip
import inspect
import os
import logging
import subprocess
import re

from analysis.plugin.public import NeedConfigWarning
from ..common import Configurator

LOGGER = logging.getLogger(__name__)


class KernelConfig(Configurator):
    """To change the kernel config"""
    _module = "KERNEL_CONFIG"
    _submod = "KERNEL_CONFIG"

    def __init__(self, user=None):
        Configurator.__init__(self, user)
        cfg_file = "/proc/config.gz"
        if os.path.isfile(cfg_file):
            self.__cfg_file = cfg_file
        else:
            self.__kernel_ver = subprocess.check_output(
                "uname -r".split()).decode().replace("\n", "")
            self.__cfg_file = "/boot/config-" + self.__kernel_ver

    def _set(self, key, value):
        if self.get(key) == value:
            return 0
        raise NeedConfigWarning(
            "Please change the kernel configuration {key} to {val}.".format(
                key=key, val=value))

    def _get(self, key):
        file_type = os.path.splitext(self.__cfg_file)[-1]
        if file_type == ".gz":
            with gzip.open(self.__cfg_file, 'rt') as file:
                cfgs = file.read()
        else:
            with open(self.__cfg_file, 'r') as file:
                cfgs = file.read()

        pattern = re.compile("^" + key + "=(.+)", re.ASCII | re.MULTILINE)
        search_obj = pattern.findall(cfgs)
        if len(search_obj) != 1:
            err = LookupError("not find one " + key)
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err
        return search_obj[0]

    def _backup(self, _, __):
        return ""

    def _resume(self, _, __):
        return None
