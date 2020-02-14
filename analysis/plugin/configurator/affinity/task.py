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
The sub class of the Configurator, used to change the affinity of tasks.
"""
import inspect
import logging
import subprocess
import re

from analysis.plugin.public import GetConfigError
from .affinityutils import Utils
from ..common import Configurator

LOGGER = logging.getLogger(__name__)


class TaskAffinity(Configurator):
    """To change the affinity of tasks"""
    _module = "AFFINITY"
    _submod = "TASK"
    _option = "taskset -p"

    def __init__(self, user=None):
        Configurator.__init__(self, user)
        self._set.__func__.__doc__ = Configurator._set.__doc__ % (
            'pid', 'cpumask in hex, no "0x" prefix, "," is permitted')

    def _get(self, key, _):
        task_id = Utils.get_task_id(key)
        if task_id is None:
            err = LookupError("Fail to find task {}".format(key))
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err

        output = subprocess.check_output(
            "{opt} {pid}".format(
                opt=self._option,
                pid=task_id).split(),
            stderr=subprocess.STDOUT)
        pattern = r"^pid.*?current affinity mask:\ (.+)"
        search_obj = re.search(
            pattern,
            output.decode(),
            re.ASCII | re.MULTILINE)
        if search_obj is None:
            err = GetConfigError("Fail to find {} affinity".format(key))
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err
        return search_obj.group(1)

    def _set(self, key, value):
        task_id = Utils.get_task_id(key)
        if task_id is None:
            err = LookupError("Fail to find task {}".format(key))
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err

        mask = value.replace(",", "")
        return subprocess.call(
            "{opt} {mask} {pid}".format(
                opt=self._option,
                mask=mask,
                pid=task_id).split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

    @staticmethod
    def check(config1, config2):
        config1 = config1.replace(",", "")
        config2 = config2.replace(",", "")
        return int(config1, base=16) == int(config2, base=16)
