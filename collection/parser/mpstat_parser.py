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
Parse the string of CPUs to a list of CPUs.
"""

from __future__ import print_function

import re

from . import base

_CPU_PATTERNS = {"single":  re.compile(r"^\s*(\d+)\s*$"),
                 "range":   re.compile(r"^\s*(\d+)\s*-\s*(\d+)\s*$"),
                 "exclude": re.compile(r"^\s*\^(\d+)\s*$")}


def _parse_cpu_str(cpu_str):
    """Parse the string of CPUs to a list of CPUs.

    @param cpu_str: the string of CPUs to parse
    @return: a list of string which represents CPU.
    """
    matches = [{key: pattern.match(sub_list) for key, pattern in _CPU_PATTERNS.items()}
               for sub_list in cpu_str.split(',')]

    includes = set()
    excludes = set()
    for match in matches:
        if match['single'] is not None:
            includes.add(int(match['single'].group(1)))
        elif match['range'] is not None:
            # in "start-end" format, both `start` and `end` are included
            includes.update(range(int(match['range'].group(1)), int(match['range'].group(2)) + 1))
        elif match['exclude'] is not None:
            excludes.add(int(match['exclude'].group(1)))
        else:
            raise ValueError("Unknown cpu str format `{}`".format(cpu_str))

    cpu_list = list(includes - excludes)
    cpu_list.sort()
    return map(str, cpu_list)


def _get_available_cpus():
    """Get the avaiable CPUs.

    @return: a list of string which represents CPU.
    """
    with open('/sys/devices/system/cpu/possible', 'r') as possible_fd:
        possible = possible_fd.read()
    return _parse_cpu_str(possible)


class MpstatParser(base.Parser):
    """The parser to parse the output of mpstat"""

    def __init__(self, raw_data_file, data_to_collect, **kwargs):
        """Initialize a mpstat parser.

        @param raw_data_file: the path of raw data
        @param data_to_collect: list of str which represents the metrics to parse
        @param dev_list: list of devices of which metrics whille be collectted
        @param alias: alias name of output fields (default: "mpstat")
        """
        base.Parser.__init__(self, raw_data_file, data_to_collect, **kwargs)

        self._dev_list = kwargs.get("dev_list", None)
        if self._dev_list == "all":
            self._dev_list = ["all"]
        elif self._dev_list == "ALL":
            self._dev_list = ["all"]
            self._dev_list.extend(_get_available_cpus())
        else:
            self._dev_list = _parse_cpu_str(self._dev_list)
        self._check_dev()

    def _check_data_to_collect(self):
        """Read the first batch output of mpstat and check whether or not all
        metrics in data_to_collect are in the output. If not, it will raise
        ValueError.
        """
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            raw_data_fd.readline()
            line_part = raw_data_fd.readline().split()
            cpu_idx = line_part.index("CPU")
            datas = line_part[cpu_idx + 1:]
        diff_set = set(self._data_to_collect) - set(datas)
        if diff_set:
            raise ValueError("`{}`: Unknown data name `{}`".format(self._raw_data_file, ','.join(diff_set)))

    def _check_dev(self):
        """Read the first batch output of mpstat and check whether or not all
        devices in dev_list are in the output. If not, it will raise ValueError.
        """
        if not self._dev_list:
            raise ValueError("You must assigned at least one device")

        devs = set()
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            raw_data_fd.readline()
            cpu_idx = raw_data_fd.readline().split().index("CPU")
            for line in raw_data_fd:
                if not line.strip():
                    continue
                dev = line.split()[cpu_idx]
                if dev in devs:
                    break
                else:
                    devs.add(dev)
        if "CPU" in devs:
            devs.remove("CPU")

        diff_set = set(self._dev_list) - devs
        if diff_set:
            raise ValueError("Can not find block device `{}`".format(','.join(diff_set)))

    def _get_iter(self):
        """Get the iteration of the mpstat parser.

        @return: the iteration of the mpstat parser
        """
        data = {}
        attrs = []
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            for row_num, line in enumerate(raw_data_fd, 2):
                if not line.strip():
                    continue
                line_part = line.split()
                if "CPU" in line_part:
                    cpu_idx = line_part.index("CPU")
                    attrs = line_part[cpu_idx + 1:]
                else:
                    if len(attrs) != len(line_part) - cpu_idx - 1:
                        print("WARNING: {}: Line {}: The number of columns may be wrong."
                              .format(self._raw_data_file, row_num))
                        return
                    line_data = [float(d) for d in line_part[cpu_idx + 1:]]
                    if line_part[cpu_idx] not in data:
                        data[line_part[cpu_idx]] = dict(zip(attrs, line_data))
                    else:
                        yield [data[dev][attr] for dev in self._dev_list for attr in self._data_to_collect]
                        data = {}
                        data[line_part[cpu_idx]] = dict(zip(attrs, line_data))
            if all(dev in data for dev in self._dev_list):
                yield [data[dev][attr] for dev in self._dev_list for attr in self._data_to_collect]
