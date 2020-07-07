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
The sub class of the Configurator, used to change the bios config.
"""
import inspect
import logging
import subprocess

from analysis.plugin.public import NeedConfigWarning
from ..common import Configurator

LOGGER = logging.getLogger(__name__)


class Bios(Configurator):
    """To change the bios config"""
    _module = "BIOS"
    _submod = "BIOS"

    def __init__(self, user=None):
        Configurator.__init__(self, user)

    def _set(self, key, value):
        raise NeedConfigWarning(
            "please change the BIOS configuration {key} to {val}".format(
                key=key, val=value))

    def _get(self, key, _):
        if key.lower() == "version":
            output_dmi = subprocess.Popen(["dmidecode", "-t", "bios"], stdout=subprocess.PIPE,
                                          shell=False)
            output_grep = subprocess.Popen(["grep", "-Po", "(?<=Version:)(.*)"],
                                           stdin=output_dmi.stdout,
                                           stdout=subprocess.PIPE,
                                           shell=False)
            output_sed = subprocess.Popen(["sed", "s/^ *//g"],
                                          stdin=output_grep.stdout,
                                          stdout=subprocess.PIPE,
                                          shell=False)
            output = subprocess.Popen(["sed", "s/ *$//g"],
                                      stdin=output_sed.stdout,
                                      stdout=subprocess.PIPE,
                                      shell=False)

            out = output.communicate()
            return bytes.decode(out[0]).strip()
        if key.lower() == "hpre_support":
            output_lspci = subprocess.Popen(["lspci"],
                                            stdout=subprocess.PIPE,
                                            shell=False)
            output = subprocess.Popen(["grep", "HPRE"],
                                      stdin=output_lspci.stdout,
                                      stdout=subprocess.PIPE,
                                      shell=False)
            out = output.communicate()
            if bytes.decode(out[0]) != "":
                return "yes"
            return "no"
        err = NotImplementedError(
            "{} can not get {}".format(
                self._module, key))
        LOGGER.error("%s.%s: %s", self.__class__.__name__,
                     inspect.stack()[0][3], str(err))
        raise err

    def _backup(self, _, __):
        return ""

    def _resume(self, _, __):
        return None
