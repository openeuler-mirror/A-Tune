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
The sub class of the monitor, used to collect the memory topo.
"""
import inspect
import logging
import subprocess
import re
import json
import dict2xml

from ..common import Monitor, get_class_type

LOGGER = logging.getLogger(__name__)


class MemTopo(Monitor):
    """To collect the memory topo"""
    _module = "MEM"
    _purpose = "TOPO"
    _option = "-c memory"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__cmd = "lshw"
        self.format.__func__.__doc__ = Monitor.format.__doc__ % ("json, table")

    def _get(self, _):
        with open('/dev/null', 'w') as no_print:
            output = subprocess.check_output("{cmd} {opt}".format(
                cmd=self.__cmd, opt=self._option).split(), stderr=no_print)
        return output.decode()

    def table_get_locator(self, bank):
        """get locator in table"""
        pattern = re.compile(
            r"DIMM.*?(\d)(\d)(\d).*",
            re.ASCII | re.MULTILINE)
        scd = pattern.findall(bank)
        if len(scd) == 0:
            err = LookupError("Fail to find data")
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err

        ret = []
        for i in scd[0]:
            ret.append(int(i))
        return ret

    def table_get_freq(self, desc):
        """get freq in table"""
        pattern = re.compile(
            r".*?(\d+)\s([KMGT]?)Hz.*?",
            re.ASCII | re.MULTILINE)
        freq = pattern.findall(desc)
        if len(freq) == 0:
            err = LookupError("Fail to find data")
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
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

    def format(self, info, fmt):
        """
        format the result of the operation
        :param info:  content that needs to be converted
        :param fmt:  converted format
        :returns output:  converted result
        """
        if fmt in ("json", "table", "xml"):
            o_json = subprocess.check_output("{cmd} -json".format(
                cmd=self.__cmd).split(), stderr=subprocess.DEVNULL)
            info = o_json.decode()
            json_content = json.loads(info)

            dict_datas = get_class_type(json_content, "memory", "System Memory")
            if fmt == "json":
                return json.dumps(dict_datas, indent=2)
            if fmt == "xml":
                return dict2xml.dict2xml(dict_datas, "topology")

            return None
        return Monitor.format(self, info, fmt)
