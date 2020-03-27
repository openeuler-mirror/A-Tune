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
Parse the string of CPUs to a list of CPUs.
"""

from __future__ import print_function

from . import base
from . import utils


class MpstatParser(base.Parser):
    """The parser to parse the output of mpstat"""

    def __init__(self, raw_data_file, data_to_collect, threshold=40.0, **kwargs):
        """Initialize a mpstat parser.

        @param raw_data_file: the path of raw data
        @param data_to_collect: list of str which represents the metrics to parse
        @param threshold: threshold to calculate %cusr and %cutil
        @param dev_list: list of devices of which metrics whille be collectted
        @param alias: alias name of output fields (default: "mpstat")
        """
        base.Parser.__init__(self, raw_data_file, data_to_collect, **kwargs)
        self.threshold = threshold

        self._dev_list = kwargs.get("dev_list", None)
        if self._dev_list == "all":
            self._dev_list = ["all"]
        elif self._dev_list == "ALL":
            self._dev_list = ["all"]
            self._dev_list.extend(utils.get_available_cpus())
        else:
            self._dev_list = utils.parse_cpu_str(self._dev_list)
        self._check_dev()

    def _get_supported_metrics(self):
        with open(self._raw_data_file, 'r') as raw_data_fd:
            raw_data_fd.readline()
            raw_data_fd.readline()
            line_part = raw_data_fd.readline().split()
            cpu_idx = line_part.index("CPU")
            return line_part[cpu_idx + 1:]

    def _get_extra_supported_metrics(self):
        return {"%util": ["%usr", "%nice", "%sys", "%iowait", "%irq", "%soft", "%steal"],
                "%cusr": ["%usr"],
                "%cutil": ["%usr", "%nice", "%sys", "%iowait", "%irq", "%soft", "%steal"]}

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
                devs.add(dev)
        if "CPU" in devs:
            devs.remove("CPU")

        diff_set = set(self._dev_list) - devs
        if diff_set:
            raise ValueError("Can not find CPU `{}` in file `{}`".format(
                ','.join(diff_set), self._raw_data_file))

    def _get_iter(self):
        """Get the iteration of the mpstat parser.

        @return: the iteration of the mpstat parser
        """
        data = {}
        attrs = []
        cpu_idx = 0
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
                        break
                    line_data = [float(d) for d in line_part[cpu_idx + 1:]]
                    if line_part[cpu_idx] in data:
                        if "all" in data:
                            data["all"]["%cusr"] = 0
                            count = len(list(filter(lambda x: x["%cusr"] != 0.0, data.values())))
                            data["all"]["%cusr"] = sum(utils["%cusr"] for utils in data.values()) \
                                                   / count if count else 0.0
                            data["all"]["%cutil"] = 0
                            count = len(list(filter(lambda x: x["%cutil"] != 0.0, data.values())))
                            data["all"]["%cutil"] = sum(utils["%cutil"] for utils in
                                                        data.values()) / count if count else 0.0
                        yield [data[dev][attr] for dev in self._dev_list
                               for attr in self._data_to_collect]
                        data.clear()
                    data[line_part[cpu_idx]] = dict(zip(attrs, line_data))
                    data[line_part[cpu_idx]]["%util"] = data[line_part[cpu_idx]]["%usr"] + \
                                                        data[line_part[cpu_idx]]["%nice"] + \
                                                        data[line_part[cpu_idx]]["%sys"] + \
                                                        data[line_part[cpu_idx]]["%irq"] + \
                                                        data[line_part[cpu_idx]]["%soft"] + \
                                                        data[line_part[cpu_idx]]["%steal"]
                    data[line_part[cpu_idx]]["%cusr"] = data[line_part[cpu_idx]]["%usr"] \
                        if data[line_part[cpu_idx]]["%usr"] >= self.threshold else 0.0
                    data[line_part[cpu_idx]]["%cutil"] = data[line_part[cpu_idx]]["%util"] \
                        if data[line_part[cpu_idx]]["%util"] >= self.threshold else 0.0
            if all(dev in data for dev in self._dev_list):
                if "all" in data:
                    data["all"]["%cusr"] = 0
                    count = len(list(filter(lambda x: x["%cusr"] != 0.0, data.values())))
                    data["all"]["%cusr"] = sum(utils["%cusr"] for utils in data.values()) / count \
                        if count else 0.0
                    data["all"]["%cutil"] = 0
                    count = len(list(filter(lambda x: x["%cutil"] != 0.0, data.values())))
                    data["all"]["%cutil"] = sum(utils["%cutil"] for utils in data.values()) \
                                            / count if count else 0.0
                yield [data[dev][attr] for dev in self._dev_list for attr in self._data_to_collect]
