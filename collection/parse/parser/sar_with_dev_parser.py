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
Sar parser with device.
"""

from __future__ import print_function

from . import base


class SarWithDevParser(base.Parser):
    """The parser to parse the output of sar with device"""

    def __init__(self, raw_data_file, data_to_collect, **kwargs):
        """Initialize a sar parser with device. The device field must be the second column.

        @param raw_data_file: the path of raw data
        @param data_to_collect: list of str which represents the metrics to parse
        @param dev_list: list of devices of which metrics whille be collectted
        @param alias: alias name of output fields (default: "sarwithdev")
        """
        base.Parser.__init__(self, raw_data_file, data_to_collect, **kwargs)
        self._dev_list = kwargs.get("dev_list", None)

    def _get_supported_metrics(self):
        """Read the first batch output of sar and get all supported metrics.

        @return: a list of string which represents the supported metrics
        """
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            raw_data_fd.readline()
            line_part = raw_data_fd.readline().split()
            return line_part[2:]

    def _check_dev(self):
        """Read the first batch output of sar and check whether or not all
        devices in dev_list are in the output. If not, it will raise ValueError.
        """
        if not self._dev_list:
            raise ValueError("You must assigned at least one device")

        devs = set()
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            raw_data_fd.readline()

            dev_field_name = raw_data_fd.readline().split()[1]
            for line in raw_data_fd:
                if not line.split():
                    continue
                dev = line.split()[1]
                if dev == dev_field_name:
                    break
                devs.add(dev)
        diff_set = set(self._dev_list) - devs
        if diff_set:
            raise ValueError("Can not find device `{}` in file `{}`".format(
                ','.join(diff_set), self._raw_data_file))

    def _get_iter(self):
        """Get the iteration of the sar parser.

        @return: the iteration of the sar parser
        """
        data = {}
        attrs = []
        extra = self._get_extra_supported_metrics()
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            row_num = 0
            for row_num, line in enumerate(raw_data_fd, 2):
                if line.strip():
                    line_part = line.split()
                    dev_field_name = line_part[1]
                    attrs = line_part[2:]
                    break
            for row_num, line in enumerate(raw_data_fd, row_num):
                if not line.strip():
                    continue
                line_part = line.split()
                if dev_field_name in line_part:
                    attrs = line_part[2:]
                else:
                    if len(attrs) != len(line_part) - 2:
                        print("WARNING: {}: Line {}: The number of columns may be wrong."
                              .format(self._raw_data_file, row_num))
                        break
                    line_data = [float(d) for d in line_part[2:]]
                    if line_part[1] in data:
                        yield [data[dev][attr] for dev in self._dev_list
                               for attr in self._data_to_collect]
                        data.clear()
                    data[line_part[1]] = dict(zip(attrs, line_data))
                    for key, dens in extra.items():
                        data[line_part[1]][key] = sum(data[line_part[1]][den] for den in dens)
            if all(dev in data for dev in self._dev_list):
                yield [data[dev][attr] for dev in self._dev_list for attr in self._data_to_collect]
