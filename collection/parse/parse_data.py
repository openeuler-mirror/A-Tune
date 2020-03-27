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
Parse data and generate csv.
"""

from __future__ import print_function
import os
import re
import csv
from itertools import chain

from parser import load_parser


def parse_data(parser_confs, yield_data_name=True, early_stop=False):
    """parse-data generator

    @param parser_confs: A list which contains the configuretion of parsers. For example,
                         [{"name": "mpstat", "data_to_collect": ["%usr", "%sys"],
                         "dev_list": ["all"]},
                          {"name": "iostat", "data_to_collect": ["rMB/s", "r_await", "%util"],
                          "dev_list": ["sdb"]},
                          ...]
    @param yield_data_name: Whether or not yield the name of fields. If yield_data_name is True,
                            then the first yield data is the names of fields
    @param early_stop: If early_stop is True and one of parsers raises StopIteration,
                       then it will raise StopIteration.
                       Otherwise, it will raise StopIteration util all parsers raise StopIteration,
                       and None will fill in suitable position if some parsers raise StopIteration
                       before that.
    @return: A generator of which `next` function will return a list contains data
             or the name of data
    """
    parsers = [load_parser(pf["name"])(**pf) for pf in parser_confs]
    if yield_data_name:
        yield list(chain.from_iterable([p.get_data_name() for p in parsers]))

    while True:
        data = []
        for parser in parsers:
            # fill with None if data in a parser is less than others
            try:
                data.extend(parser.get_next_data())
            except StopIteration:
                if early_stop:
                    return
                data.extend([None] * parser.get_data_num())
        # if all data is None, then stop
        if all(d is None for d in data):
            return
        yield data


def _get_path_map(data_dir, name_filters):
    raw_data_logs = os.listdir(data_dir)
    pattern = re.compile(r"(.*)-({})-(\d{{8}}-\d{{6}}).log".format('|'.join(name_filters)))
    matches = [pattern.match(p) for p in raw_data_logs]
    path_map = {}
    for match in matches:
        if not match:
            continue
        if match.group(1) not in path_map:
            path_map[match.group(1)] = {}
        if match.group(3) not in path_map[match.group(1)]:
            path_map[match.group(1)][match.group(3)] = {}
        path_map[match.group(1)][match.group(3)][match.group(2)] = \
            os.path.join(data_dir, match.group(0))
    return path_map


def _generate_csv(conf, workload, csv_path):
    with open(csv_path, 'w') as csv_writer_fd:
        csv_writer = csv.writer(csv_writer_fd)
        for result in parse_data(**conf):
            result.append(workload)
            csv_writer.writerow(result)
    print("generate {} successfully".format(csv_path))


def generate_csv(input_dir, output_dir, **kwargs):
    """generate all csv for raw logs in intput_dir.

    @param input_dir: the path of raw logs
    @param output_dir: the output dir of csv
    @param block_dev: the block device of which the metrics will be collected (default: 'sda')
    @param net_dev: the network device of which the metrics will be collected (default: 'eth0')
    @param workload: the workload type of the data (default: 'default')
    @param interval: the sample interval in seconds (default: 1)
    """
    parse_conf = {
        'early_stop': True,
        'yield_data_name': False,
        'parser_confs':
            [
                {
                    'name': 'mpstat',
                    'data_to_collect': ['%usr', '%nice', '%sys', '%iowait', '%irq', '%soft',
                                        '%steal', '%guest', '%cutil'],
                    'threshold': 30.0,
                    'dev_list': 'all',
                    'alias': 'cpu'
                },
                {
                    'name': 'iostat',
                    'data_to_collect': ['r/s', 'w/s', 'rMB/s', 'wMB/s', '%rrqm', '%wrqm',
                                        'rareq-sz', 'wareq-sz', 'r_await', 'w_await',
                                        '%util', 'blk_sat'],
                    'skip_first': True,
                    'alias': 'io',
                },
                {
                    'name': 'sar-with-dev',
                    'data_to_collect': ['rxkB/s', 'txkB/s', 'rxpck/s', 'txpck/s', '%ifutil'],
                    'skip_first': True,
                    'alias': 'sar-network'
                },
                {
                    'name': 'sar-edev',
                    'data_to_collect': ['err/s', 'net_sat'],
                    'alias': 'sar-net_err'
                },
                {
                    'name': 'meminfo',
                    'data_to_collect': ['Util'],
                    'alias': 'mem'
                },
                {
                    'name': 'perf-mem',
                    'data_to_collect': ['MEM_Total', 'MEM_BW_Util'],
                    'interval': kwargs.get('interval', 1),
                    'alias': 'perf-memBW',
                },
                {
                    'name': 'perf-cpu',
                    'data_to_collect': ['IPC', 'LLC', 'MPKI', 'ITLB', 'DTLB', 'StallBackend/Insts',
                                        'StallBackend/cycles', 'Memory_Bound', 'Store_Bound'],
                    'alias': 'perf-cpu',
                },
                {
                    'name': 'vmstat',
                    'data_to_collect': ['b', 'swpd', 'free', 'buff', 'cache', 'bi', 'bo', 'in',
                                        'cs', 'mem_sat', 'cpu_util', 'cpu_sat'],
                    'skip_first': True,
                    'alias': 'vmstat',
                },
                {
                    'name': 'sar',
                    'data_to_collect': ['proc/s', 'cswch/s'],
                    'alias': 'sar-task'
                },
                {
                    'name': 'sar',
                    'data_to_collect': ['runq-sz', 'plist-sz', 'ldavg-1', 'ldavg-5', 'ldavg-15'],
                    'alias': 'sar-load'
                },
                {
                    'name': 'sysctl',
                    'data_to_collect': ['task-util', 'file-util'],
                    'alias': 'sysctl'
                }
            ]
    }
    path_map = _get_path_map(input_dir, ("mpstat", "iostat", "vmstat", "meminfo", "perf-cpu",
                                         "perf-memBW", "sar-network", "sar-net_err", "sar-task",
                                         "sar-load", "sysctl"))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for benchmark, value in path_map.items():
        for tag, paths in value.items():
            parse_conf["yield_data_name"] = False
            parse_conf["early_stop"] = True
            for parser_conf in parse_conf["parser_confs"]:
                if parser_conf["name"] in ("perf-mem", "sar", "sar-with-dev", "sar-edev"):
                    parser_conf["raw_data_file"] = paths[parser_conf["alias"]]
                else:
                    parser_conf["raw_data_file"] = paths[parser_conf["name"]]
                if parser_conf["name"] == "iostat":
                    parser_conf["dev_list"] = [kwargs.get("block_dev", "sda")]
                if parser_conf["alias"] in ("sar-network", "sar-net_err"):
                    parser_conf["dev_list"] = [kwargs.get("net_dev", "eth0")]

            _generate_csv(parse_conf, kwargs.get("workload", "default"),
                          os.path.join(output_dir, "{}-{}.csv".format(benchmark, tag)))


if __name__ == "__main__":
    import argparse

    ARG_PARSER = argparse.ArgumentParser(description="parser output of mpstat, iostat, nicstat ...",
                                         formatter_class=lambda prog:
                                         argparse.HelpFormatter(prog, max_help_position=80))
    ARG_PARSER.add_argument('input', metavar='input',
                            help='input dir')
    ARG_PARSER.add_argument('output', metavar='output',
                            help='output dir')
    ARG_PARSER.add_argument('-b', '--block', metavar='DEV', default='sda', help='block device')
    ARG_PARSER.add_argument('-n', '--net', metavar='DEV', default='eth0', help='net device')
    ARG_PARSER.add_argument('-w', '--workload', metavar='WORKLOAD', default='idle',
                            help='workload type')
    ARG_PARSER.add_argument('-i', '--interval', metavar='SECONDS', type=int, default=5,
                            help='sample interval')

    ARGS = ARG_PARSER.parse_args()
    generate_csv(ARGS.input, ARGS.output, block_dev=ARGS.block, net_dev=ARGS.net,
                 workload=ARGS.workload, interval=ARGS.interval)
