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
The parser to parse the output of perf-mem.sh.
"""

from __future__ import division
from __future__ import print_function
from . import base
from . import utils


class PerfMemParser(base.Parser):
    """The parser to parse the output of perf-mem.sh"""

    def __init__(self, raw_data_file, data_to_collect, interval=1, **kwargs):
        """Initialize a perf parser.

        @param raw_data_file: the path of raw data
        @param data_to_collect: list of str which represents the metrics to parse
        @param interval: the interval time of data. It is only for perf-mem.sh.
        @param mem_bw: max memory bandwidth
        @param alias: alias name of output fields (default: "perf")
        """
        base.Parser.__init__(self, raw_data_file, data_to_collect, **kwargs)

        self._mem_bw = kwargs.get("mem_bw", -1)
        self._interval = interval

    def _get_supported_metrics(self):
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            return raw_data_fd.readline().split()

    def _get_extra_supported_metrics(self):
        return {"MEM_BW_Util": ["MEM_Total"]}

    def _get_iter(self):
        """Get the iteration of the perf parser.

        @return: the iteration of the perf parser
        """
        if self._mem_bw < 0:
            self._mem_bw = utils.get_theory_memory_bandwidth()
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            attrs = raw_data_fd.readline().split()
            for row_num, line in enumerate(raw_data_fd, 3):
                line_part = line.split()
                line_data = [float(d[:-1]) / self._interval for d in line_part]
                if len(attrs) != len(line_data):
                    print("WARNING: {}: Line {}: The number of columns may be wrong."
                          .format(self._raw_data_file, row_num))
                    break
                data = dict(zip(attrs, line_data))
                data["MEM_BW_Util"] = data["MEM_Total"] / self._mem_bw * 100
                yield [data[attr] for attr in self._data_to_collect]
