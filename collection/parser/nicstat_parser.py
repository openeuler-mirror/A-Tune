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
The parser to parse the output of nicstat.
"""

from __future__ import print_function

from . import base

class NicstatParser(base.Parser):

    """The parser to parse the output of nicstat"""

    def __init__(self, raw_data_file, data_to_collect, skip_first=True, **kwargs):
        """Initialize a nicstat parser.

        @param raw_data_file: the path of raw data
        @param data_to_collect: list of str which represents the metrics to parse
        @param dev_list: list of devices of which metrics whille be collectted
        @param skip_first: skip the first batch of data or not. Bacause the first
                           output of nicstat is the statistics information since
                           boot, we can skip it.
        @param alias: alias name of output fields (default: "nicstat")
        """
        base.Parser.__init__(self, raw_data_file, data_to_collect, **kwargs)

        self._dev_list = kwargs.get("dev_list", None)
        self._check_dev()

        # the first output of nicstat is the statistics information since boot, so we can skip it
        if skip_first:
            self.get_next_data()

    def _check_data_to_collect(self):
        """Read the first batch output of nicstat and check whether or not all
        metrics in data_to_collect are in the output. If not, it will raise
        ValueError.
        """
        with open(self._raw_data_file, 'r') as raw_data_fd:
            line = raw_data_fd.readline()
            datas = line.split()[2:]
        diff_set = set(self._data_to_collect) - set(datas)
        if diff_set:
            raise ValueError("`{}`: Unknown data name `{}`".format(self._raw_data_file, ','.join(diff_set)))

    def _check_dev(self):
        """Read the first batch output of nicstat and check whether or not all
        devices in dev_list are in the output. If not, it will raise ValueError.
        """
        if not self._dev_list:
            raise ValueError("You must assigned at least one device")

        devs = set()
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            for line in raw_data_fd:
                line_part = line.split()
                if line_part[0] == "Time":
                    break
                else:
                    devs.add(line_part[1])
        diff_set = set(self._dev_list) - devs
        if diff_set:
            raise ValueError("Can not find nic device `{}`".format(','.join(diff_set)))

    def _get_iter(self):
        """Get the iteration of the mpstat parser.

        @return: the iteration of the mpstat parser
        """
        data = {}
        attrs = []
        first_line = True
        with open(self._raw_data_file, 'r') as raw_data_fd:
            for row_num, line in enumerate(raw_data_fd, 1):
                line_part = line.strip().split()
                if line_part[0] == "Time":
                    if first_line:
                        first_line = False
                    else:
                        yield [data[dev][attr] for dev in self._dev_list for attr in self._data_to_collect]
                    attrs = line_part[2:]
                    data.clear()
                else:
                    if len(attrs) != len(line_part) - 2:
                        print("WARNING: {}: Line {}: The number of columns may be wrong."
                              .format(self._raw_data_file, row_num))
                        return
                    data[line_part[1]] = dict(zip(attrs, [float(d) for d in line_part[2:]]))
            if data:
                yield [data[dev][attr] for dev in self._dev_list for attr in self._data_to_collect]
