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
The sub class of the monitor, used to collect the nic topo.
"""

import subprocess
import json
import dict2xml

from ..common import Monitor, get_class_type


class NetTopo(Monitor):
    """To collect the nic topo"""
    _module = "NET"
    _purpose = "TOPO"
    _option = "-c network"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__cmd = "lshw"
        self.format.__func__.__doc__ = Monitor.format.__doc__ % ("xml, json")

    def _get(self, _):
        with open('/dev/null', 'w') as no_print:
            output = subprocess.check_output("{cmd} {opt}".format(
                cmd=self.__cmd, opt=self._option).split(), stderr=no_print)
        return output.decode()

    def format(self, info, fmt):
        """
        format the result of the operation
        :param info:  content that needs to be converted
        :param fmt:  converted format
        :returns output:  converted result
        """
        if fmt in ("json", "xml"):
            o_json = subprocess.check_output("{cmd} -json".format(
                cmd=self.__cmd).split(), stderr=subprocess.DEVNULL)
            info = o_json.decode()
            json_content = json.loads(info)

            dict_datas = get_class_type(json_content, "network")
            if fmt == "json":
                return json.dumps(dict_datas, indent=2)
            if fmt == "xml":
                return dict2xml.dict2xml(dict_datas, "topology")
            return None
        return Monitor.format(self, info, fmt)
