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

    def _check_data_to_collect(self):
        """Read the first batch output of get_meminfo.sh and check whether or
        not all metrics in data_to_collect are in the output. If not, it will
        raise ValueError.
        """
        with open(self._raw_data_file) as csv_fd:
            reader = csv.reader(csv_fd)
            header = next(reader)
        header.append("HugePages")
        header.append("MemUsed")
        diff_set = set(self._data_to_collect) - set(header)
        if diff_set:
            raise ValueError("`{}`: Unknown data name `{}`".format(self._raw_data_file, ','.join(diff_set)))

    def _get_iter(self):
        """Get the iteration of the iostat parser.

        @return: the iteration of the iostat parser
        """
        with open(self._raw_data_file) as csv_fd:
            reader = csv.DictReader(csv_fd, quoting=csv.QUOTE_NONNUMERIC)
            for row in reader:
                data = []
                for data_name in self._data_to_collect:
                    if data_name == "HugePages":
                        data.append(row["HugePages_Total"] - row["HugePages_Free"])
                    elif data_name == "MemUsed":
                        data.append(row["MemTotal"] - row["MemFree"] - row["Hugepagesize"] * row["HugePages_Free"])
                    else:
                        data.append(row[data_name])
                yield data
