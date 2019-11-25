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
The sub class of the monitor, used to collect memory bandwidth stat info.
"""

import sys
import logging
import subprocess
import getopt
import re
import json

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from monitor.common import *
from monitor.memory import topo

logger = logging.getLogger(__name__)


class MemBandwidth(Monitor):
    """To collect memory bandwidth stat info"""
    _module = "MEM"
    _purpose = "BANDWIDTH"
    _option = "-a -e {events} --interval-print {int} --interval-count 1"

    __evs1620 = {
        "c0d0c0_r": "hisi_sccl1_ddrc0/flux_rd/",
        "c0d0c1_r": "hisi_sccl1_ddrc1/flux_rd/",
        "c0d0c2_r": "hisi_sccl1_ddrc2/flux_rd/",
        "c0d0c3_r": "hisi_sccl1_ddrc3/flux_rd/",
        "c0d0c0_w": "hisi_sccl1_ddrc0/flux_wr/",
        "c0d0c1_w": "hisi_sccl1_ddrc1/flux_wr/",
        "c0d0c2_w": "hisi_sccl1_ddrc2/flux_wr/",
        "c0d0c3_w": "hisi_sccl1_ddrc3/flux_wr/",
        "c0d1c0_r": "hisi_sccl3_ddrc0/flux_rd/",
        "c0d1c1_r": "hisi_sccl3_ddrc1/flux_rd/",
        "c0d1c2_r": "hisi_sccl3_ddrc2/flux_rd/",
        "c0d1c3_r": "hisi_sccl3_ddrc3/flux_rd/",
        "c0d1c0_w": "hisi_sccl3_ddrc0/flux_wr/",
        "c0d1c1_w": "hisi_sccl3_ddrc1/flux_wr/",
        "c0d1c2_w": "hisi_sccl3_ddrc2/flux_wr/",
        "c0d1c3_w": "hisi_sccl3_ddrc3/flux_wr/",
        "c1d0c0_r": "hisi_sccl5_ddrc0/flux_rd/",
        "c1d0c1_r": "hisi_sccl5_ddrc1/flux_rd/",
        "c1d0c2_r": "hisi_sccl5_ddrc2/flux_rd/",
        "c1d0c3_r": "hisi_sccl5_ddrc3/flux_rd/",
        "c1d0c0_w": "hisi_sccl5_ddrc0/flux_wr/",
        "c1d0c1_w": "hisi_sccl5_ddrc1/flux_wr/",
        "c1d0c2_w": "hisi_sccl5_ddrc2/flux_wr/",
        "c1d0c3_w": "hisi_sccl5_ddrc3/flux_wr/",
        "c1d1c0_r": "hisi_sccl7_ddrc0/flux_rd/",
        "c1d1c1_r": "hisi_sccl7_ddrc1/flux_rd/",
        "c1d1c2_r": "hisi_sccl7_ddrc2/flux_rd/",
        "c1d1c3_r": "hisi_sccl7_ddrc3/flux_rd/",
        "c1d1c0_w": "hisi_sccl7_ddrc0/flux_wr/",
        "c1d1c1_w": "hisi_sccl7_ddrc1/flux_wr/",
        "c1d1c2_w": "hisi_sccl7_ddrc2/flux_wr/",
        "c1d1c3_w": "hisi_sccl7_ddrc3/flux_wr/"}

    __cnt1620 = {
        "Total": 0,
        "CPU0": 0,
        "CPU1": 0,
        "CPU0_Die0": 0,
        "CPU0_Die1": 0,
        "CPU1_Die0": 0,
        "CPU1_Die1": 0,
        "CPU0_Die0_R": 0,
        "CPU0_Die1_R": 0,
        "CPU1_Die0_R": 0,
        "CPU1_Die1_R": 0,
        "CPU0_Die0_W": 0,
        "CPU0_Die1_W": 0,
        "CPU1_Die0_W": 0,
        "CPU1_Die1_W": 0,
        "Total_Max": 0,
        "CPU0_Max": 0,
        "CPU1_Max": 0,
        "Total_Util": 0}

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__cmd = "perf stat"
        self.__interval = 1000

        self.__evs = self.__evs1620
        self.__cnt = self.__cnt1620
        self.__cnt["CPU0_Max"] = self.__get_theory_bandwidth(0) / 1024 / 1024
        self.__cnt["CPU1_Max"] = self.__get_theory_bandwidth(1) / 1024 / 1024

        self.__events = ""
        for e in self.__evs:
            self.__events = self.__events + self.__evs[e] + ","
        self.__events = self.__events.strip(",")

        help_info = "--fields="
        for c in self.__cnt:
            help_info = help_info + c + "/"
        help_info = help_info.strip("/")
        self.decode.__func__.__doc__ = Monitor.decode.__doc__ % (help_info)

    def _get(self, para=None):
        if para is not None:
            opts, args = getopt.getopt(para.split(), None, ['interval='])
            for opt, val in opts:
                if opt in ('--interval'):
                    if val.isdigit():
                        self.__interval = int(val) * 1000
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
                    int=self.__interval,
                    events=self.__events)).split(),
            stderr=subprocess.STDOUT)
        return output.decode()

    def __get_theory_bandwidth(self, socket):
        memtopo = topo.MemTopo()
        info_json = memtopo.report("json", None)
        info = json.loads(info_json)

        width = 0
        dimms = [[0 for i in range(8)] for i in range(8)]
        for dimm in info["memorys"][0]["children"]:
            if dimm.get("size") is None:
                continue
            locator = memtopo._table_get_locator(dimm["slot"])
            if dimms[locator[0]][locator[1]] == 0:
                dimms[locator[0]][locator[1]] = dimm["width"] * \
                    memtopo._table_get_freq(dimm["description"]) / 8
        ret = 0
        for channel in dimms[socket]:
            ret += channel
        return ret

    def __read_counters(self, c_evs):
        self.__cnt["CPU0_Die0_R"] = ((int(c_evs["c0d0c0_r"]) + int(c_evs["c0d0c1_r"]) + int(
            c_evs["c0d0c2_r"]) + int(c_evs["c0d0c3_r"])) * 32 / 1024 / 1024) * 1000 / self.__interval
        self.__cnt["CPU0_Die1_R"] = ((int(c_evs["c0d1c0_r"]) + int(c_evs["c0d1c1_r"]) + int(
            c_evs["c0d1c2_r"]) + int(c_evs["c0d1c3_r"])) * 32 / 1024 / 1024) * 1000 / self.__interval
        self.__cnt["CPU1_Die0_R"] = ((int(c_evs["c1d0c0_r"]) + int(c_evs["c1d0c1_r"]) + int(
            c_evs["c1d0c2_r"]) + int(c_evs["c1d0c3_r"])) * 32 / 1024 / 1024) * 1000 / self.__interval
        self.__cnt["CPU1_Die1_R"] = ((int(c_evs["c1d1c0_r"]) + int(c_evs["c1d1c1_r"]) + int(
            c_evs["c1d1c2_r"]) + int(c_evs["c1d1c3_r"])) * 32 / 1024 / 1024) * 1000 / self.__interval
        self.__cnt["CPU0_Die0_W"] = ((int(c_evs["c0d0c0_w"]) + int(c_evs["c0d0c1_w"]) + int(
            c_evs["c0d0c2_w"]) + int(c_evs["c0d0c3_w"])) * 32 / 1024 / 1024) * 1000 / self.__interval
        self.__cnt["CPU0_Die1_W"] = ((int(c_evs["c0d1c0_w"]) + int(c_evs["c0d1c1_w"]) + int(
            c_evs["c0d1c2_w"]) + int(c_evs["c0d1c3_w"])) * 32 / 1024 / 1024) * 1000 / self.__interval
        self.__cnt["CPU1_Die0_W"] = ((int(c_evs["c1d0c0_w"]) + int(c_evs["c1d0c1_w"]) + int(
            c_evs["c1d0c2_w"]) + int(c_evs["c1d0c3_w"])) * 32 / 1024 / 1024) * 1000 / self.__interval
        self.__cnt["CPU1_Die1_W"] = ((int(c_evs["c1d1c0_w"]) + int(c_evs["c1d1c1_w"]) + int(
            c_evs["c1d1c2_w"]) + int(c_evs["c1d1c3_w"])) * 32 / 1024 / 1024) * 1000 / self.__interval
        self.__cnt["CPU0_Die0"] = self.__cnt["CPU0_Die0_R"] + \
            self.__cnt["CPU0_Die0_W"]
        self.__cnt["CPU0_Die1"] = self.__cnt["CPU0_Die1_R"] + \
            self.__cnt["CPU0_Die1_W"]
        self.__cnt["CPU1_Die0"] = self.__cnt["CPU1_Die0_R"] + \
            self.__cnt["CPU1_Die0_W"]
        self.__cnt["CPU1_Die1"] = self.__cnt["CPU1_Die1_R"] + \
            self.__cnt["CPU1_Die1_W"]
        self.__cnt["CPU0"] = self.__cnt["CPU0_Die0_R"] + self.__cnt["CPU0_Die0_W"] + \
            self.__cnt["CPU0_Die1_R"] + self.__cnt["CPU0_Die1_W"]
        self.__cnt["CPU1"] = self.__cnt["CPU1_Die0_R"] + self.__cnt["CPU1_Die0_W"] + \
            self.__cnt["CPU1_Die1_R"] + self.__cnt["CPU1_Die1_W"]
        self.__cnt["Total"] = self.__cnt["CPU0"] + self.__cnt["CPU1"]
        self.__cnt["Total_Max"] = self.__cnt["CPU0_Max"] + self.__cnt["CPU1_Max"]
        self.__cnt["Total_Util"] = self.__cnt["Total"] / self.__cnt["Total_Max"] * 100

    def decode(self, info, para):
        if para is None:
            return info

        c_evs = self.__evs.copy()
        for e in self.__evs:
            pattern = "^\ {2,}(\d.*?)\ {2,}(\d.*?)\ {2,}(" + \
                self.__evs[e] + ").*?"
            searchObj = re.search(pattern, info, re.ASCII | re.MULTILINE)
            if searchObj is not None:
                c_evs[e] = searchObj.group(2).replace(",", "")
            else:
                err = LookupError("Fail to find {}".format(self.__evs[e]))
                logger.error(
                    "{}.{}: {}".format(
                        self.__class__.__name__,
                        sys._getframe().f_code.co_name,
                        str(err)))
                raise err

        self.__read_counters(c_evs)
        fields = []
        ret = ""

        opts, args = getopt.getopt(para.split(), None, ['fields='])
        for opt, val in opts:
            if opt in ('--fields'):
                fields.append(val)
                continue

        for f in fields:
            ret = ret + " {:.2f}".format(self.__cnt[f])
        return ret


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: ' + sys.argv[0] + ' fmt path')
        sys.exit(-1)
    ct = MemBandwidth("UT")
#	help(ct)
    ct.report(sys.argv[1], sys.argv[2], "--interval=5;--fields=Total --fields=CPU0 --fields=CPU1 --fields=Total_Max --fields=CPU0_Max --fields=CPU1_Max --fields=Total_Util")
