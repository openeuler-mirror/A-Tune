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
Vmstat parser.
"""

from __future__ import print_function
from __future__ import division

import multiprocessing
from . import base


class VmstatParser(base.Parser):
    """The parser to parse the output of vmstat"""

    def __init__(self, raw_data_file, data_to_collect, skip_first=True, **kwargs):
        """Initialize a vmstat parser.

        @param raw_data_file: the path of raw data
        @param data_to_collect: list of str which represents the metrics to parse
        @param skip_first: skip the first batch of data or not. Bacause the first
                           output of vmstat is the statistics information since
                           boot, we can skip it.
        @param cpu_count: the number of CPUs when gather the raw log
        @param alias: alias name of output fields (default: "iostat")
        """
        base.Parser.__init__(self, raw_data_file, data_to_collect, **kwargs)
        self.cpu_count = kwargs.get("cpu_count", multiprocessing.cpu_count())

        # the first output of vmstat is the statistics information since boot, so we can skip it
        if skip_first:
            self.get_next_data()

    def _get_supported_metrics(self):
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            return raw_data_fd.readline().split()

    def _get_extra_supported_metrics(self):
        return {"free_delta": ["free"], "buff_delta": ["buff"], "cache_delta": ["cache"],
                "cpu_util": ["us", "sy", "st"], "cpu_sat": ["r"], "mem_sat": ["si", "so"]}

    def _get_iter(self):
        """Get the iteration of the vmstat parser.

        @return: the iteration of the vmstat parser
        """
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            attrs = raw_data_fd.readline().split()
            for row_num, line in enumerate(raw_data_fd, 3):
                line_part = line.split()
                line_data = [int(d) for d in line_part]
                if len(attrs) != len(line_data):
                    print("WARNING: {}: Line {}: The number of columns may be wrong."
                          .format(self._raw_data_file, row_num))
                    break
                data = dict(zip(attrs, line_data))
                if row_num == 3:
                    free_init, buff_init, cache_init = data["free"], data["buff"], data["cache"]
                # extra metrics
                data["free_delta"] = free_init - data["free"]
                data["buff_delta"] = data["buff"] - buff_init
                data["cache_delta"] = data["cache"] - cache_init
                data["cpu_util"] = data["us"] + data["sy"] + data["st"]
                data["cpu_sat"] = data["r"]
                data["mem_sat"] = data["si"] + data["so"]
                yield [data[attr] for attr in self._data_to_collect]
