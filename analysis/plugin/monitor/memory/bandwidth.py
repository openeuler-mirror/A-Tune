#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-10-29

"""
The sub class of the monitor, used to collect memory bandwidth stat info.
"""
import inspect
import logging
import subprocess
import getopt
import re
import json

from ..common import Monitor
from ..memory import topo

LOGGER = logging.getLogger(__name__)


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

        all_events = subprocess.check_output(
            "perf list".split(),
            shell=False,
            stderr=subprocess.STDOUT).decode()
        self.__events = ""
        for event in self.__evs:
            search_obj = re.search(self.__evs[event], all_events, re.ASCII | re.MULTILINE)
            if search_obj is not None:
                self.__events = self.__events + self.__evs[event] + ","
        self.__events = self.__events.strip(",")
        LOGGER.info("events is %s", self.__events)

        help_info = "--fields="
        for cnt in self.__cnt:
            help_info = help_info + cnt + "/"
        help_info = help_info.strip("/")
        self.decode.__func__.__doc__ = Monitor.decode.__doc__ % help_info

    def _get(self, para=None):
        if para is not None:
            opts, _ = getopt.getopt(para.split(), None, ['interval='])
            for opt, val in opts:
                if opt in '--interval':
                    if val.isdigit():
                        self.__interval = int(val) * 1000
                    else:
                        err = ValueError(
                            "Invalid parameter: {opt}={val}".format(
                                opt=opt, val=val))
                        LOGGER.error("%s.%s: %s", self.__class__.__name__,
                                     inspect.stack()[0][3], str(err))
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

    @staticmethod
    def __get_theory_bandwidth(socket):
        memtopo = topo.MemTopo()
        info_json = memtopo.report("json", None)
        if isinstance(info_json, Exception):
            raise info_json
        info = json.loads(info_json)

        dimms = [[0 for i in range(8)] for i in range(8)]
        for dimm in info["memorys"][0]["children"]:
            if dimm.get("size") is None:
                continue
            locator = memtopo.table_get_locator(dimm["slot"])
            if dimms[locator[0]][locator[1]] == 0:
                dimms[locator[0]][locator[1]] = dimm["width"] * \
                                                memtopo.table_get_freq(dimm["description"]) / 8
        ret = 0
        for channel in dimms[socket]:
            ret += channel
        return ret

    def __read_counters(self, c_evs):
        self.__cnt["CPU0_Die0_R"] = ((int(c_evs["c0d0c0_r"]) + int(c_evs["c0d0c1_r"]) + int(
            c_evs["c0d0c2_r"]) + int(c_evs["c0d0c3_r"])) * 32 / 1024 / 1024) * 1000 / \
                                    self.__interval
        self.__cnt["CPU0_Die1_R"] = ((int(c_evs["c0d1c0_r"]) + int(c_evs["c0d1c1_r"]) + int(
            c_evs["c0d1c2_r"]) + int(c_evs["c0d1c3_r"])) * 32 / 1024 / 1024) * 1000 / \
                                    self.__interval
        self.__cnt["CPU1_Die0_R"] = ((int(c_evs["c1d0c0_r"]) + int(c_evs["c1d0c1_r"]) + int(
            c_evs["c1d0c2_r"]) + int(c_evs["c1d0c3_r"])) * 32 / 1024 / 1024) * 1000 / \
                                    self.__interval
        self.__cnt["CPU1_Die1_R"] = ((int(c_evs["c1d1c0_r"]) + int(c_evs["c1d1c1_r"]) + int(
            c_evs["c1d1c2_r"]) + int(c_evs["c1d1c3_r"])) * 32 / 1024 / 1024) * 1000 / \
                                    self.__interval
        self.__cnt["CPU0_Die0_W"] = ((int(c_evs["c0d0c0_w"]) + int(c_evs["c0d0c1_w"]) + int(
            c_evs["c0d0c2_w"]) + int(c_evs["c0d0c3_w"])) * 32 / 1024 / 1024) * 1000 / \
                                    self.__interval
        self.__cnt["CPU0_Die1_W"] = ((int(c_evs["c0d1c0_w"]) + int(c_evs["c0d1c1_w"]) + int(
            c_evs["c0d1c2_w"]) + int(c_evs["c0d1c3_w"])) * 32 / 1024 / 1024) * 1000 / \
                                    self.__interval
        self.__cnt["CPU1_Die0_W"] = ((int(c_evs["c1d0c0_w"]) + int(c_evs["c1d0c1_w"]) + int(
            c_evs["c1d0c2_w"]) + int(c_evs["c1d0c3_w"])) * 32 / 1024 / 1024) * 1000 / \
                                    self.__interval
        self.__cnt["CPU1_Die1_W"] = ((int(c_evs["c1d1c0_w"]) + int(c_evs["c1d1c1_w"]) + int(
            c_evs["c1d1c2_w"]) + int(c_evs["c1d1c3_w"])) * 32 / 1024 / 1024) * 1000 / \
                                    self.__interval
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
        """
        decode the result of the operation
        :param info:  content that needs to be decoded
        :param para:  command line argument
        :returns ret:  operation result
        """
        if para is None:
            return info

        c_evs = self.__evs.copy()
        for evs in self.__evs:
            pattern = r"^\ {2,}(\d.*?)\ {2,}(\d.*?)\ {2,}(" + \
                      self.__evs[evs] + ").*?"
            search_obj = re.search(pattern, info, re.ASCII | re.MULTILINE)
            if search_obj is not None:
                c_evs[evs] = search_obj.group(2).replace(",", "")
            else:
                c_evs[evs] = 0

        self.__read_counters(c_evs)
        fields = []
        ret = ""

        opts, _ = getopt.getopt(para.split(), None, ['fields='])
        for opt, val in opts:
            if opt in '--fields':
                fields.append(val)
                continue

        for field in fields:
            ret = ret + " {:.2f}".format(self.__cnt[field])
        return ret
