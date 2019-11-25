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

import sys
import logging
import os
import subprocess
import random

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from configurator.common import *

logger = logging.getLogger(__name__)


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
            "bash {script} {val}".format(
                script=script,
                val=value).split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True)
        if len(output.stderr) != 0:
            err = UserWarning(name + ": " + output.stderr.decode())
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err
        return 0

    def _get(self, key):
        name = os.path.basename(key)
        script = "{}/get.sh".format(key)
        output = subprocess.run(
            "bash {script}".format(
                script=script).split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True)
        if len(output.stderr) != 0:
            err = UserWarning(name + ": " + output.stderr.decode())
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err
        return output.stdout.decode()

    def _check(self, config1, config2):
        return True

    def _backup(self, key, rollback_info):
        name = os.path.basename(key)
        script = "{}/backup.sh".format(key)
        if os.path.isfile(script):
            output = subprocess.run(
                "bash {script} {rb_info} {ver}".format(
                    script=script,
                    rb_info=rollback_info,
                    ver=random.random()).split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True)
            if len(output.stderr) != 0:
                err = UserWarning(name + ": " + output.stderr.decode())
                logger.error(
                    "{}.{}: {}".format(
                        self.__class__.__name__,
                        sys._getframe().f_code.co_name,
                        str(err)))
                raise err
            return output.stdout.decode()
        else:
            return Configurator._backup(self, key, rollback_info)

    def _resume(self, key, value):
        name = os.path.basename(key)
        script = "{}/resume.sh".format(key)
        if os.path.isfile(script):
            output = subprocess.run(
                "bash {script} {val}".format(
                    script=script,
                    val=value).split(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=True)
            if len(output.stderr) != 0:
                err = UserWarning(name + ": " + output.stderr.decode())
                logger.error(
                    "{}.{}: {}".format(
                        self.__class__.__name__,
                        sys._getframe().f_code.co_name,
                        str(err)))
                raise err
            return 0
        else:
            return Configurator._resume(self, key, value)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: ' + sys.argv[0] + ' script_file=value')
        sys.exit(-1)
    ct = Script("UT")
    print(ct.set(sys.argv[1]))
    print(ct.get(ct._getcfg(sys.argv[1])[0]))
