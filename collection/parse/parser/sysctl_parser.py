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
# Create: 2019-11-22

"""
The parser to parse the output of get_sysctl.sh
"""

from __future__ import division

import re
import csv

from . import base


class SysctlParser(base.Parser):
    """The parser to parse the output of get_sysctl.sh"""

    def __init__(self, raw_data_file, data_to_collect, **kwargs):
        """Initialize a meminfo parser.

        @param raw_data_file: the path of raw data
        @param data_to_collect: list of str which represents the metrics to parse
        @param alias: alias name of output fields (default: "meminfo")
        """
        base.Parser.__init__(self, raw_data_file, data_to_collect, **kwargs)

    def _get_supported_metrics(self):
        with open(self._raw_data_file) as csv_fd:
            reader = csv.reader(csv_fd)
            return next(reader)

    def _get_extra_supported_metrics(self):
        return {"threads-max": ["/proc/sys/kernel/threads-max"],
                "file-open": ["/proc/sys/fs/file-nr"],
                "file-free": ["/proc/sys/fs/file-nr"],
                "file-max": ["/proc/sys/fs/file-nr"],
                "runq-sz": ["/proc/loadavg"],
                "plist-sz": ["/proc/loadavg"],
                "ldavg-1": ["/proc/loadavg"],
                "ldavg-5": ["/proc/loadavg"],
                "ldavg-15": ["/proc/loadavg"],
                "last-pid": ["/proc/loadavg"],
                "task-util": ["/proc/loadavg", "/proc/sys/kernel/threads-max"],
                "file-util": ["/proc/sys/fs/file-nr"],
                }

    def _get_iter(self):
        with open(self._raw_data_file) as csv_fd:
            reader = csv.DictReader(csv_fd)
            for row in reader:
                data = {}
                data["threads-max"] = int(row["/proc/sys/kernel/threads-max"])
                data["file-open"], data["file-free"], data["file-max"] = \
                    [int(d) for d in row["/proc/sys/fs/file-nr"].split()]
                data["ldavg-1"], data["ldavg-5"], data["ldavg-15"], \
                data["runq-sz"], data["plist-sz"], data["last-pid"] = \
                    [t(d) for t, d in zip((float, float, float, int, int, int),
                                          re.split(r"\s+|/", row["/proc/loadavg"]))]
                data["task-util"] = data["plist-sz"] / data["threads-max"] * 100
                data["file-util"] = data["file-open"] / data["file-max"] * 100
                yield [data[attr] for attr in self._data_to_collect]
