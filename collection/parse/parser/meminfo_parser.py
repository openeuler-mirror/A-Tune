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
The parser to parse the output of get_meminfo.sh.
"""

import csv

from . import base


class MeminfoParser(base.Parser):
    """The parser to parse the output of get_meminfo.sh"""

    def __init__(self, raw_data_file, data_to_collect, **kwargs):
        """Initialize a meminfo parser.

        @param raw_data_file: the path of raw data
        @param data_to_collect: list of str which represents the metrics to parse
        @param alias: alias name of output fields (default: "meminfo")
        """
        base.Parser.__init__(self, raw_data_file, data_to_collect, **kwargs)

    def _get_supported_metrics(self):
        """read the first batch output of get_meminfo.sh and get all supported metrics.

        @return: a list of string which represents the supported metrics
        """
        with open(self._raw_data_file) as csv_fd:
            reader = csv.reader(csv_fd)
            return next(reader)

    def _get_extra_supported_metrics(self):
        return {"HugePages": ["HugePages_Total", "HugePages_Free"],
                "MemUsed": ["MemTotal", "MemFree", "Hugepagesize", "HugePages_Free"],
                "Util": ["MemTotal", "MemFree", "Hugepagesize", "HugePages_Free"],
                }

    def _get_iter(self):
        """Get the iteration of the meminfo parser.

        @return: the iteration of the meminfo parser
        """
        with open(self._raw_data_file) as csv_fd:
            reader = csv.DictReader(csv_fd, quoting=csv.QUOTE_NONNUMERIC)
            for data in reader:
                data["HugePages"] = data["HugePages_Total"] - data["HugePages_Free"]
                data["MemUsed"] = data["MemTotal"] - data["MemFree"] - \
                                  data["Hugepagesize"] * data["HugePages_Free"]
                data["Util"] = (data["MemTotal"] - data["MemFree"] - data["Buffers"] - \
                                data["Cached"] - data["Slab"]) / data["MemTotal"] * 100
                yield [data[attr] for attr in self._data_to_collect]
