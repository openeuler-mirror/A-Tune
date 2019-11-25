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
The sub class of the monitor, used to collect the system BIOS info.
"""

import sys
import logging
import subprocess
import json
import dict2xml

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from monitor.common import *

logger = logging.getLogger(__name__)


class SysBiosInfo(Monitor):
    """To collect the system BIOS info"""
    _module = "SYS"
    _purpose = "BIOS"
    _option = "-c system"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__cmd = "lshw"
        self.format.__func__.__doc__ = Monitor.format.__doc__ % ("xml, json")

    def _get(self, para=None):
        with open('/dev/null', 'w') as no_print:
            output = subprocess.check_output("{cmd} {opt}".format(
                cmd=self.__cmd, opt=self._option).split(),
                stderr=no_print)
        return output.decode()

    def format(self, info, fmt):
        if (fmt == "json") or (fmt == "xml"):
            o_json = subprocess.check_output("{cmd} -json".format(
                cmd=self.__cmd).split(), stderr=subprocess.DEVNULL)
            info = o_json.decode()
            all = json.loads(info)

            datas = []
            walk_class_type(all, "memory", "BIOS", datas)
            all.pop("children")
            datas.append(all)
            dict_datas = {}
            dict_datas["BIOS"] = datas
            if (fmt == "json"):
                return json.dumps(dict_datas, indent=2)
            elif (fmt == "xml"):
                return dict2xml.dict2xml(dict_datas, "info")
        else:
            return Monitor.format(self, info, fmt)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: ' + sys.argv[0] + ' fmt path')
        sys.exit(-1)
    ct = SysBiosInfo("UT")
    ct.report(sys.argv[1], sys.argv[2])
