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

import sys
import logging
import subprocess
import re

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from configurator.common import *

logger = logging.getLogger(__name__)


class TaskAffinity(Configurator):
    """To change the affinity of tasks"""
    _module = "AFFINITY"
    _submod = "TASK"
    _option = "taskset -p"

    def __init__(self, user=None):
        Configurator.__init__(self, user)
        self._set.__func__.__doc__ = Configurator._set.__doc__ % (
            'pid or task_name', 'cpumask in hex, no "0x" prefix, "," is permitted')

    def __get_task_id(self, key):
        if key.isdecimal():
            id = key
            name = None
        else:
            id = None
            name = key.replace("(", "\(")
            name = name.replace(")", "\)")

        if id is None:
            output = subprocess.check_output("ps -e".split(),
                                             stderr=subprocess.STDOUT)
            pattern = "^\ *(\d.*?)\ +(.*?)\ +(.*?)\ +" + name
            searchObj = re.search(
                pattern,
                output.decode(),
                re.ASCII | re.MULTILINE)
            if searchObj is not None:
                id = searchObj.group(1)
        return id

    def _get(self, key):
        id = self.__get_task_id(key)
        if id is None:
            err = LookupError("Fail to find task {}".format(key))
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err

        output = subprocess.check_output(
            "{opt} {pid}".format(
                opt=self._option,
                pid=id).split(),
            stderr=subprocess.STDOUT)
        pattern = "^pid.*?current affinity mask:\ (.+)"
        searchObj = re.search(
            pattern,
            output.decode(),
            re.ASCII | re.MULTILINE)
        if searchObj is None:
            err = GetConfigError("Fail to find {} affinity".format(key))
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err
        return searchObj.group(1)

    def _set(self, key, value):
        id = self.__get_task_id(key)
        if id is None:
            err = LookupError("Fail to find task {}".format(key))
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err

        mask = value.replace(",", "")
        return subprocess.call(
            "{opt} {mask} {pid}".format(
                opt=self._option,
                mask=mask,
                pid=id).split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

    def _check(self, config1, config2):
        config1 = config1.replace(",", "")
        config2 = config2.replace(",", "")
        return int(config1, base=16) == int(config2, base=16)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: ' + sys.argv[0] + ' key=value')
        sys.exit(-1)
    ct = TaskAffinity("UT")
    print(ct.set(sys.argv[1]))
    print(ct.get(ct._getcfg(sys.argv[1])[0]))
