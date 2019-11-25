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
The sub class of the monitor, used to collect the memory topo.
"""

import sys
import logging
import subprocess
import re
import json
import prettytable
import dict2xml

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from monitor.common import *

logger = logging.getLogger(__name__)


class MemTopo(Monitor):
    """To collect the memory topo"""
    _module = "MEM"
    _purpose = "TOPO"
    _option = "-c memory"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__cmd = "lshw"
        self.format.__func__.__doc__ = Monitor.format.__doc__ % ("json, table")

    def _get(self, para=None):
        with open('/dev/null', 'w') as no_print:
            output = subprocess.check_output("{cmd} {opt}".format(
                cmd=self.__cmd, opt=self._option).split(),
                stderr=no_print)
        return output.decode()

    def __table_init(self, column):
        self.__columns = column
        data = ['Socket', 'Channel']
        for i in range(self.__columns):
            data.append("Slot {}".format(i))
        return prettytable.PrettyTable(data)

    def _table_get_locator(self, bank):
        pattern = re.compile(
            "DIMM.*?(\d)(\d)(\d)\s.*",
            re.ASCII | re.MULTILINE)
        scd = pattern.findall(bank)
        if len(scd) == 0:
            err = LookupError("Fail to find data")
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err

        ret = []
        for i in scd[0]:
            ret.append(int(i))
        return ret

    def _table_get_freq(self, desc):
        pattern = re.compile(
            ".*?(\d+)\s([KMGT]?)Hz.*?",
            re.ASCII | re.MULTILINE)
        freq = pattern.findall(desc)
        if len(freq) == 0:
            err = LookupError("Fail to find data")
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err

        if freq[-1][1] == "K":
            ret = int(freq[-1][0]) * 1000
        elif freq[-1][1] == "M":
            ret = int(freq[-1][0]) * 1000000
        elif freq[-1][1] == "G":
            ret = int(freq[-1][0]) * 1000000000
        elif freq[-1][1] == "T":
            ret = int(freq[-1][0]) * 1000000000000
        else:
            ret = int(freq[-1][0])
        return ret

    def __table_add_banks(self, table, datas, i, j):
        data = [i, j]
        for k in range(self.__columns):
            data.append(datas[i][j][k])
        table.add_row(data)

    def format(self, info, fmt):
        if (fmt == "json") or (fmt == "table") or (fmt == "xml"):
            o_json = subprocess.check_output("{cmd} -json".format(
                cmd=self.__cmd).split(), stderr=subprocess.DEVNULL)
            info = o_json.decode()
            all = json.loads(info)

            dict_datas = get_class_type(all, "memory", "System Memory")
            if (fmt == "json"):
                return json.dumps(dict_datas, indent=2)
            elif (fmt == "xml"):
                return dict2xml.dict2xml(dict_datas, "topology")

            dimms = [[["NO DIMM" for i in range(8)]
                      for i in range(8)] for i in range(8)]
            max_socket = 0
            max_slot = 0
            max_channel = 0
            datas = dict_datas["memorys"]
            for data in datas:
                for bank in data["children"]:
                    locator = self._table_get_locator(bank["slot"])
                    if locator[0] > max_socket:
                        max_socket = locator[0]
                    if locator[1] > max_channel:
                        max_channel = locator[1]
                    if locator[2] > max_slot:
                        max_slot = locator[2]
                    if "size" in bank.keys():
                        dimms[locator[0]][locator[1]][locator[2]] = "{} {} {} {}".format(
                            bank["vendor"], bank["description"], bank["size"], bank["units"])

            tables = ""
            for socket in range(max_socket + 1):
                table = self.__table_init(max_slot + 1)
                for channel in range(max_channel + 1):
                    self.__table_add_banks(table, dimms, socket, channel)
                tables += table.get_string(hrules=prettytable.ALL) + "\n\n"
            return tables
        else:
            return Monitor.format(self, info, fmt)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: ' + sys.argv[0] + ' fmt path')
        sys.exit(-1)
    ct = MemTopo("UT")
    print(ct.report(sys.argv[1], sys.argv[2]))
