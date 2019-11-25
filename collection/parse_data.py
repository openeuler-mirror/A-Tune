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


def generate_csv(input_dir, output_dir, block_dev, net_dev, workload):
    parse_conf = {
        'early_stop': True,
        'yield_data_name': False,
        'parser_confs':
        [
            {
                'name': 'mpstat',
                'raw_data_file': '',
                'data_to_collect': ['%usr', '%sys', '%iowait', '%irq', '%guest'],
                'dev_list': 'all',
                'alias': 'cpu'
            }, {
                'name': 'iostat',
                'raw_data_file': '',
                'data_to_collect': ['rMB/s', 'wMB/s', '%util'],
                'dev_list': [],
                'skip_first': True,
                'alias': 'io',
            }, {
                'name': 'sar-with-dev',
                'raw_data_file': '',
                'data_to_collect': ['rxkB/s', 'txkB/s', 'rxpck/s', 'txpck/s', '%ifutil'],
                'dev_list': [],
                'skip_first': True,
                'alias': 'sar-network'
            }, {
                'name': 'perf',
                'raw_data_file': '',
                'data_to_collect': ['IPC', 'MPKI', "LLC", "ITLB", "DTLB"],
                'interval': 1,
                'alias': 'perf-cpu',
            }, {
                'name': 'perf',
                'raw_data_file': '',
                'data_to_collect': ['MEM_Total'],
                'interval': 5,
                'alias': 'perf-memBW',
            }
        ]
    }
    raw_data_logs = os.listdir(input_dir)
    pattern = re.compile(r"(.*)-(mpstat|iostat|vmstat|meminfo|perf-cpu|perf-memBW|sar-network)-(\d{8}-\d{6}).log")
    matches = [pattern.match(p) for p in raw_data_logs]
    path_map = {}
    for match in matches:
        if not match:
            continue
        if match.group(1) not in path_map:
            path_map[match.group(1)] = {}
        if match.group(3) not in path_map[match.group(1)]:
            path_map[match.group(1)][match.group(3)] = {}
        path_map[match.group(1)][match.group(3)][match.group(2)] = os.path.join(input_dir, match.group(0))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for benchmark, vb in path_map.items():
        for tag, paths in vb.items():
            parse_conf["yield_data_name"] = False
            parse_conf["early_stop"] = True
            for parser_conf in parse_conf["parser_confs"]:
                if parser_conf["name"] in ("perf", "sar-with-dev"):
                    parser_conf["raw_data_file"] = paths[parser_conf["alias"]]
                else:
                    parser_conf["raw_data_file"] = paths[parser_conf["name"]]
                if parser_conf["name"] == "iostat":
                    parser_conf["dev_list"] = [block_dev]
                if parser_conf["alias"] in ("sar-network", "sar-net_err"):
                    parser_conf["dev_list"] = [net_dev]

            csv_path = os.path.join(output_dir, "{}-{}.csv".format(benchmark, tag))
            with open(csv_path, 'w') as fd:
                csv_writer = csv.writer(fd)
                for result in parse_data(**parse_conf):
                    result.append(workload)
                    csv_writer.writerow(result)
            print("generate {} successfully".format(csv_path))


if __name__ == "__main__":
    import argparse

    arg_parser = argparse.ArgumentParser(description="parser output of mpstat, iostat, nicstat ...",
                                         formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=80))
    arg_parser.add_argument('input', metavar='input',
                            help='input dir')
    arg_parser.add_argument('output', metavar='output',
                            help='output dir')
    arg_parser.add_argument('-b', '--block', metavar='DEV', default='sda', help='block device')
    arg_parser.add_argument('-n', '--net', metavar='DEV', default='eth0', help='net device')
    arg_parser.add_argument('-w', '--workload', metavar='WORKLOAD', default='idle', help='workload type')

    args = arg_parser.parse_args()
    generate_csv(args.input, args.output, args.block, args.net, args.workload)
