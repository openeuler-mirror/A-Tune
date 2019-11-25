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
The sub class of the Configurator, used to change the grub2 config.
"""

import sys
import logging
import os
import subprocess
import random
import shutil
import re
from bootutils import Utils
if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from configurator.common import *

logger = logging.getLogger(__name__)


class Grub2(Configurator):
    """To change the grub2 config"""
    _module = "BOOTLOADER"
    _submod = "GRUB2"

    def __init__(self, user=None):
        Configurator.__init__(self, user)
        __cfg_files = ["/etc/grub2.cfg", "/etc/grub2-efi.cfg"]
        for f in __cfg_files:
            if os.path.isfile(f):
                self.__cfg_file = f
                break
        self.__kernel_ver = subprocess.check_output("uname -r".split()).decode(
        ).replace("\n", "")

    def __get_cfg_entry(self, version):
        with open(self.__cfg_file, 'r') as f:
            ctx = f.read()
        pattern = re.compile(
            "\n(menuentry)[^\{\}]*?\{[^\{\}]*?\n\s+(linux)[^\{\}]*?" +
            version.replace(
                ".",
                "\.") +
            "[^\{\}]*?(\})",
            re.ASCII | re.DOTALL)
        searchObj = pattern.search(ctx)
        start = searchObj.span(1)
        cmd = searchObj.span(2)
        end = searchObj.span(3)
        return {"START": start[0], "CMD": cmd[0], "END": end[1]}

    def _get(self, key):
        entry = self.__get_cfg_entry(self.__kernel_ver)
        with open(self.__cfg_file, 'r') as f:
            f.seek(entry["CMD"])
            cmd = f.readline()

        keypos = Utils.get_keypos(cmd, key)
        if keypos == -1:
            err = GetConfigError("Fail to find {} config".format(key))
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err

        config = cmd[keypos:].split()[0]
        if config.find("=") != -1:
            return config.split("=")[1]
        else:
            return None

    @pre_check(
        Configurator._precheck,
        os.path.split(
            os.path.realpath(__file__))[0] +
        "/grub2.json")
    def _set(self, key, value):
        entry = self.__get_cfg_entry(self.__kernel_ver)
        if value is None:
            new = key
        else:
            new = "{key}={val}".format(key=key, val=value)

        with open(self.__cfg_file, 'r+') as f:
            f.seek(entry["CMD"])
            cmd = f.readline()

            keypos = Utils.get_keypos(cmd, key)
            if keypos != -1:
                old = cmd[keypos:].split("\n")[0].split()[0]
                file_modify(f, entry["CMD"] + keypos,
                            entry["CMD"] + keypos + len(old) - 1, new)
            else:
                file_modify(f, entry["CMD"] + len(cmd) - 1, -1, " " + new)

        active = Utils.get_value(key)
        if value == active:
            return 0
        raise NeedRebootWarning(
            "Need reboot to make the config change of grub2 effect.")

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
        print('usage: ' + sys.argv[0] + ' key[=value]')
        sys.exit(-1)
    ct = Grub2("UT1")
    save = ct.backup(sys.argv[1], "./1/")
    print(save)
    print(ct.set(sys.argv[1]))
    print(ct.get(ct._getcfg(sys.argv[1])[0]))
    print(ct.resume(save))
