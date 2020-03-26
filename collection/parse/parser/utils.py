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
Utilities for parsers
"""

from __future__ import division

import json
import re
import analysis.plugin.monitor.memory.topo as topo

_CPU_PATTERNS = {"single": re.compile(r"^\s*(\d+)\s*$"),
                 "range": re.compile(r"^\s*(\d+)\s*-\s*(\d+)\s*$"),
                 "exclude": re.compile(r"^\s*\^(\d+)\s*$"),
                 "all": re.compile(r"^\s*all\s*$")}


def parse_cpu_str(cpu_str):
    """Parse the string of CPUs to a list of CPUs.

    @param cpu_str: the string of CPUs to parse
    @return: a list of string which represents CPU.
    """
    matches = [{key: pattern.match(sub_list) for key, pattern in _CPU_PATTERNS.items()}
               for sub_list in cpu_str.split(',')]

    includes = set()
    excludes = set()
    containes_all = False
    for match in matches:
        if match['single'] is not None:
            includes.add(int(match['single'].group(1)))
        elif match['range'] is not None:
            # in "start-end" format, both `start` and `end` are included
            includes.update(range(int(match['range'].group(1)), int(match['range'].group(2)) + 1))
        elif match['exclude'] is not None:
            excludes.add(int(match['exclude'].group(1)))
        elif match['all'] is not None:
            containes_all = True
        else:
            raise ValueError("Unknown cpu str format `{}`".format(cpu_str))

    cpu_list = list(includes - excludes)
    cpu_list.sort()
    if containes_all:
        cpu_list.insert(0, 'all')
    return list(map(str, cpu_list))


def get_available_cpus():
    """Get the avaiable CPUs.

    @return: a list of string which represents CPU.
    """
    with open('/sys/devices/system/cpu/possible', 'r') as possible_fd:
        possible = possible_fd.read()
    return parse_cpu_str(possible)


def get_theory_memory_bandwidth():
    """Get the theory memory bandwidth.

    @return: theory memory bandwidth
    """
    memtopo = topo.MemTopo()
    info_json = memtopo.report("json", None)
    if isinstance(info_json, Exception):
        raise info_json
    info = json.loads(info_json)

    dimms = [[0 for _ in range(8)] for _ in range(8)]
    for dimm in info["memorys"][0]["children"]:
        if dimm.get("size") is None:
            continue
        locator = memtopo.table_get_locator(dimm["slot"])
        if dimms[locator[0]][locator[1]] == 0:
            dimms[locator[0]][locator[1]] = dimm["width"] * \
                                            memtopo.table_get_freq(dimm["description"]) / 8
    return (sum(dimms[0]) + sum(dimms[1])) / 1024 / 1024
