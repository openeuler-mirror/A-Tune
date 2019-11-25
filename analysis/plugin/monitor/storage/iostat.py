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
The sub class of the monitor, used to collect the storage stat info.
"""

import sys
import logging
import subprocess
import getopt
import re

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from monitor.common import *

logger = logging.getLogger(__name__)


class IoStat(Monitor):
    """To collect the storage stat info"""
    _module = "STORAGE"
    _purpose = "STAT"
    _option = "-xmt {int} 2"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__cmd = "iostat"
        self.__interval = 1
        self.format.__func__.__doc__ = Monitor.format.__doc__ % ("json")
        self.decode.__func__.__doc__ = Monitor.decode.__doc__ % (
            "--device=x, --fields=dev/rs/ws/rMBs/wMBs/rrqms/wrqms/rrqm/wrqm/r_await/w_await/aqu-sz/rareq-sz/wareq-sz/svctm/util")

    def _get(self, para=None):
        if para is not None:
            opts, args = getopt.getopt(para.split(), None, ['interval='])
            for opt, val in opts:
                if opt in ('--interval'):
                    if val.isdigit():
                        self.__interval = int(val)
                    else:
                        err = ValueError(
                            "Invalid parameter: {opt}={val}".format(
                                opt=opt, val=val))
                        logger.error(
                            "{}.{}: {}".format(
                                self.__class__.__name__,
                                sys._getframe().f_code.co_name,
                                str(err)))
                        raise err
                    continue

        output = subprocess.check_output(
            "{cmd} {opt}".format(
                cmd=self.__cmd,
                opt=self._option.format(
                    int=self.__interval)).split())
        return output.decode()

    def format(self, info, fmt):
        if (fmt == "json"):
            o_json = subprocess.check_output(
                "{cmd} -o JSON {opt}".format(
                    cmd=self.__cmd, opt=self._option.format(
                        int=self.__interval)).split())
            return o_json.decode()
        else:
            return Monitor.format(self, info, fmt)

    def decode(self, info, para):
        if para is None:
            return info

        keyword = {"dev": 0,
                   "rs": 1,
                   "ws": 2,
                   "rMBs": 3,
                   "wMBs": 4,
                   "rrqms": 5,
                   "wrqms": 6,
                   "rrqm": 7,
                   "wrqm": 8,
                   "r_await": 9,
                   "w_await": 10,
                   "aqu-sz": 11,
                   "rareq-sz": 12,
                   "wareq-sz": 13,
                   "svctm": 14,
                   "util": 15}

        keys = []
        dev = "sd.*?"
        ret = ""

        opts, args = getopt.getopt(para.split(), None, ['device=', 'fields='])
        for opt, val in opts:
            if opt in ('--device'):
                dev = val
                continue
            if opt in ('--fields'):
                keys.append(keyword[val])
                continue

        pattern = re.compile(
            "^(" +
            dev +
            ")\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)\ {1,}(\d*\.\d*)",
            re.ASCII | re.MULTILINE)
        searchObj = pattern.findall(info)
        if len(searchObj) == 0:
            err = LookupError("Fail to find data for {}".format(dev))
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err

        for i in keys:
            ret = ret + " " + searchObj[-1][i]
        return ret


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: ' + sys.argv[0] + ' fmt path')
        sys.exit(-1)
    ct = IoStat("UT")
    ct.report(
        sys.argv[1],
        sys.argv[2],
        "--interval=2;--fields=wMBs --fields=rMBs")
