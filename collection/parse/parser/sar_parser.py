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
# Create: 2019-11-22

"""
The parser to parse the output of sar without device
"""

from __future__ import print_function

from . import base


class SarParser(base.Parser):
    """The parser to parse the output of sar without device"""

    def __init__(self, raw_data_file, data_to_collect, **kwargs):
        """Initialize a sar parser.

        @param raw_data_file: the path of raw data
        @param data_to_collect: list of str which represents the metrics to parse
        @param alias: alias name of output fields (default: "sar")
        """
        base.Parser.__init__(self, raw_data_file, data_to_collect, **kwargs)

    def _get_supported_metrics(self):
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            raw_data_fd.readline()
            # the first column is time
            return raw_data_fd.readline().split()[1:]

    def _get_iter(self):
        """Get the iteration of the sar parser.

        @return: the iteration of the sar parser
        """
        start = False
        attrs = []
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            for row_num, line in enumerate(raw_data_fd, 2):
                if not line.strip():
                    start = True
                    continue
                if "Average" in line:
                    return
                line_part = line.split()
                if start:
                    attrs = line_part[1:]
                    start = False
                    continue
                line_data = [float(d) for d in line_part[1:]]
                if len(attrs) != len(line_data):
                    print("WARNING: {}: Line {}: The number of columns may be wrong."
                          .format(self._raw_data_file, row_num))
                    break
                data = dict(zip(attrs, line_data))
                yield [data[attr] for attr in self._data_to_collect]
