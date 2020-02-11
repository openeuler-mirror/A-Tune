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
The sub class of the Configurator, used to extend script for CPI.
"""
import inspect
import logging
import os
import subprocess
import random

from analysis.plugin.public import GetConfigError
from ..common import Configurator

LOGGER = logging.getLogger(__name__)


class Script(Configurator):
    """The script extention of CPI"""
    _module = "SCRIPT"
    _submod = "SCRIPT"

    def __init__(self, user=None):
        Configurator.__init__(self, user)

    def _set(self, key, value):
        name = os.path.basename(key)
        script = "{}/set.sh".format(key)
        output = subprocess.run(
            "{script} {val}".format(
                script=script,
                val=value).split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            shell=False,
            check=True)
        if len(output.stderr) != 0:
            err = UserWarning(name + ": " + output.stderr.decode())
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err
        return 0

    def _get(self, key, value):
        name = os.path.basename(key)
        script = "{}/get.sh".format(key)
        if not os.path.exists(script):
            raise GetConfigError("script {} not implement".format(script))

        output = subprocess.run(
            "{script} {val}".format(
                script=script,
                val=value).split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            check=True)
        if len(output.stderr) != 0:
            err = UserWarning(name + ": " + output.stderr.decode())
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err
        return output.stdout.decode()

    @staticmethod
    def check(_, __):
        return True

    def _backup(self, config, rollback_info):
        name = os.path.basename(config)
        script = "{}/backup.sh".format(config)
        if os.path.isfile(script):
            output = subprocess.run(
                "{script} {rb_info} {ver}".format(
                    script=script,
                    rb_info=rollback_info,
                    ver=random.random()).split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                check=True)
            if len(output.stderr) != 0:
                err = UserWarning(name + ": " + output.stderr.decode())
                LOGGER.error("%s.%s: %s", self.__class__.__name__,
                             inspect.stack()[0][3], str(err))
                raise err
            return output.stdout.decode()
        return Configurator._backup(self, config, rollback_info)

    def _resume(self, key, value):
        name = os.path.basename(key)
        script = "{}/resume.sh".format(key)
        if os.path.isfile(script):
            output = subprocess.run(
                "{script} {val}".format(
                    script=script,
                    val=value).split(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                shell=False,
                check=True)
            if len(output.stderr) != 0:
                err = UserWarning(name + ": " + output.stderr.decode())
                LOGGER.error("%s.%s: %s", self.__class__.__name__,
                             inspect.stack()[0][3], str(err))
                raise err
            return 0
        return Configurator._resume(self, key, value)
