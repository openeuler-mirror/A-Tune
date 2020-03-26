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
The sub class of the monitor, used to collect the perf stat info.
"""
import inspect
import logging
import subprocess
import getopt
import re
from ..common import Monitor

LOGGER = logging.getLogger(__name__)


class PerfStat(Monitor):
    """To collect the perf stat info"""
    _module = "PERF"
    _purpose = "STAT"
    _option = "-a -e cycles,instructions,branches,branch-misses,cache-misses,cache-references," \
              "dTLB-load-misses,dTLB-loads,iTLB-load-misses,iTLB-loads,stalled-cycles-backend," \
              "r7004,r7005 --interval-print {int} --interval-count 1"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__cmd = "perf stat"
        self.__interval = 1000

        self.__stat = {
            "cycles": 0,
            "instructions": 0,
            "branches": 0,
            "branch-misses": 0,
            "cache-misses": 0,
            "cache-references": 0,
            "dTLB-load-misses": 0,
            "dTLB-loads": 0,
            "iTLB-load-misses": 0,
            "iTLB-loads": 0,
            "stalled-cycles-backend": 0,
            "memstall-load": 0,
            "memstall-store": 0,
            "IPC": 0,
            "BRANCH-MISS-RATIO": 0,
            "CACHE-MISS-RATIO": 0,
            "DTLB-LOAD-MISS-RATIO": 0,
            "ITLB-LOAD-MISS-RATIO": 0,
            "MPKI": 0,
            "SBPI": 0,
            "SBPC": 0,
            "MEMORY-BOUND": 0,
            "STORE-BOUND": 0}

        help_info = "--fields="
        for stat in self.__stat:
            help_info = help_info + stat + "/"
        help_info = help_info.strip("/")
        self.decode.__func__.__doc__ = Monitor.decode.__doc__ % (help_info)

    def _get(self, para=None):
        if para is not None:
            opts, _ = getopt.getopt(para.split(), None, ['interval='])
            for opt, val in opts:
                if opt in '--interval':
                    if val.isdigit():
                        self.__interval = int(val) * 1000
                    else:
                        err = ValueError("Invalid parameter: {opt}={val}".format(opt=opt, val=val))
                        LOGGER.error("%s.%s: %s", self.__class__.__name__,
                                     inspect.stack()[0][3], str(err))
                        raise err
                    continue

        output = subprocess.check_output(
            "{cmd} {opt}".format(
                cmd=self.__cmd,
                opt=self._option.format(
                    int=self.__interval)).split(),
            stderr=subprocess.STDOUT)
        return output.decode()

    def decode(self, info, para):
        """
        decode the result of the operation
        :param info:  content that needs to be decoded
        :param para:  command line argument
        :returns ret:  operation result
        """
        if para is None:
            return info

        keyword = {"time": 0,
                   "counts": 1,
                   "unit": 2,
                   "events": 3}

        eventmap = {"memstall-load": "r7004",
                    "memstall-store": "r7005"}

        keys = []
        ret = ""

        opts, _ = getopt.getopt(para.split(), None, ['fields='])
        for opt, val in opts:
            if opt in '--fields':
                keys.append(val)
                continue

        for stat in self.__stat:
            event = eventmap.get(stat)
            if event is None:
                event = stat
            pattern = r"^\ {2,}(\d.*?)\ {2,}(\d.*?)\ {2,}(\w*)\ {2,}(" + \
                      event + r")\ {1,}.*"
            search_obj = re.search(pattern, info, re.ASCII | re.MULTILINE)
            if search_obj is not None:
                self.__stat[stat] = int(search_obj.group(keyword["counts"] + 1).replace(",", ""))
            else:
                self.__stat[stat] = -1

        self.__stat["IPC"] = self.__stat["instructions"] / \
                             self.__stat["cycles"]
        self.__stat["BRANCH-MISS-RATIO"] = self.__stat["branch-misses"] / \
                                           self.__stat["branches"] * 100
        self.__stat["CACHE-MISS-RATIO"] = self.__stat["cache-misses"] / \
                                          self.__stat["cache-references"] * 100
        self.__stat["DTLB-LOAD-MISS-RATIO"] = self.__stat["dTLB-load-misses"] / \
                                              self.__stat["dTLB-loads"] * 100
        self.__stat["ITLB-LOAD-MISS-RATIO"] = self.__stat["iTLB-load-misses"] / \
                                              self.__stat["iTLB-loads"] * 100
        self.__stat["MPKI"] = self.__stat["cache-misses"] / \
                              self.__stat["instructions"] * 1000
        self.__stat["SBPI"] = self.__stat["instructions"] / \
                              self.__stat["instructions"]
        self.__stat["SBPC"] = self.__stat["instructions"] / \
                              self.__stat["cycles"]
        self.__stat["MEMORY-BOUND"] = (self.__stat["memstall-load"] +
                                       self.__stat["memstall-store"]) / \
                                      self.__stat["cycles"] * 100
        self.__stat["STORE-BOUND"] = self.__stat["memstall-store"] / \
                                     self.__stat["cycles"] * 100

        for event in keys:
            ret = ret + " " + str(self.__stat[event])

        return ret
