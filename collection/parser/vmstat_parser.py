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
Vmstat parser.
"""

from __future__ import print_function

from . import base


class VmstatParser(base.Parser):
    """Docstring for VmstatParser. """

    def __init__(self, raw_data_file, data_to_collect, skip_first=True, **kwargs):
        """Initialize a vmstat parser.

        @param raw_data_file: the path of raw data
        @param data_to_collect: list of str which represents the metrics to parse
        @param skip_first: skip the first batch of data or not. Bacause the first
                           output of vmstat is the statistics information since
                           boot, we can skip it.
        @param alias: alias name of output fields (default: "iostat")
        """
        base.Parser.__init__(self, raw_data_file, data_to_collect, **kwargs)

        # the first output of vmstat is the statistics information since boot, so we can skip it
        if skip_first:
            self.get_next_data()

    def _check_data_to_collect(self):
        """Read the first batch output of vmstat and check whether or not all
        metrics in data_to_collect are in the output. If not, it will raise
        ValueError.
        """
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            datas = raw_data_fd.readline().split()
        diff_set = set(self._data_to_collect) - set(datas)
        if diff_set:
            raise ValueError("`{}`: Unknown data name `{}`".format(self._raw_data_file, ','.join(diff_set)))

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
                    return
                data = dict(zip(attrs, line_data))
                yield [data[attr] for attr in self._data_to_collect]
