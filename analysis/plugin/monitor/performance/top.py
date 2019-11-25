#!/usr/bin/env python3
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
The sub class of the monitor, used to collect the perf top snapshot.
"""

import sys
import logging
import subprocess
import getopt
import re
import random

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from monitor.common import *

logger = logging.getLogger(__name__)


class PerfTop(Monitor):
    """To collect the perf top snapshot"""
    _module = "PERF"
    _purpose = "TOP"
    _option = "-a -e {event} sleep {int}"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__interval = 1
        self.__event = "cycles"
        self.__keyword = {"overhead": 0,
                          "command": 1,
                          "object": 2,
                          "symbol": 3}

        help_info = "--interval, --event"
        self._get.__func__.__doc__ = Monitor._get.__doc__ % (help_info)

        help_info = "--fields="
        for f in self.__keyword:
            help_info = help_info + f + "/"
        help_info = help_info.strip("/")
        self.decode.__func__.__doc__ = Monitor.decode.__doc__ % (help_info)

    def _get(self, para=None):
        if para is not None:
            opts, args = getopt.getopt(
                para.split(), None, [
                    'interval=', 'event='])
            for opt, val in opts:
                if opt in ('--interval'):
                    if val.isdigit():
                        self.__interval = int(val)
                    else:
                        err = ValueError(
                            "Invalid parameter: {opt}={val}".format(
                                opt=opt, val=val))
                        logger.error(
                            "{}.{}: {}".format(
                                self.__class__.__name__,
                                sys._getframe().f_code.co_name,
                                str(err)))
                        raise err
                    continue
                elif opt in ('--event'):
                    self.__event = val.split(",")[-1]
                    continue

        data_file = "/tmp/perf{}".format(random.random())
        subprocess.check_output(
            "perf record -o {data} {opt}".format(
                opt=self._option.format(
                    event=self.__event,
                    int=self.__interval),
                data=data_file).split(),
            stderr=subprocess.DEVNULL)
        output = subprocess.check_output("perf report --stdio -i {data}".format(
            data=data_file).split(),
            stderr=subprocess.STDOUT)
        return output.decode()

    def __add_merge_entry(self, merge, entry, mask):
        entry = list(entry)
        entry[self.__keyword["overhead"]] = float(
            entry[self.__keyword["overhead"]])
        entry[self.__keyword["symbol"]] = int(
            entry[self.__keyword["symbol"]], 16)

        for i in range(len(merge)):
            if (merge[i][self.__keyword["command"]] == entry[self.__keyword["command"]]) and (
                    merge[i][self.__keyword["object"]] == entry[self.__keyword["object"]]):
                entry_addr = entry[self.__keyword["symbol"]] & ~mask
                merged_addr = merge[i][self.__keyword["symbol"]] & ~mask
                if entry_addr == merged_addr:
                    merge[i][self.__keyword["overhead"]
                             ] += entry[self.__keyword["overhead"]]
                    merge[i][self.__keyword["symbol"]] = merged_addr
                    return

        merge.append(entry)
        return

    def __addr_merge(self, info, mask):
        merge = []
        i = 0
        while True:
            try:
                int(info[i][self.__keyword["symbol"]], 16)
            except ValueError:
                i += 1
                continue
            except IndexError:
                break
            self.__add_merge_entry(merge, info.pop(i), mask)

        for i in range(len(merge)):
            merge[i][self.__keyword["overhead"]
                     ] = "%2.2f" % merge[i][self.__keyword["overhead"]]
            merge[i][self.__keyword["symbol"]
                     ] = "0x%016x" % merge[i][self.__keyword["symbol"]]
            info.append(merge[i])
        return

    def decode(self, info, para):
        if para is None:
            return info

        pattern = re.compile(
            "^\ {2,}(\d.*?)%\ {2,}(\w.*?)\ {1,}(.*?)\ {2,}\[[.|k]\]\ (\w.*)",
            re.ASCII | re.MULTILINE)
        searchObj = pattern.findall(info)
        if len(searchObj) == 0:
            err = LookupError("Fail to find data")
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err

        keys = []
        opts, args = getopt.getopt(
            para.split(), None, [
                'fields=', 'addr-merge='])
        for opt, val in opts:
            if opt in ('--fields'):
                keys.append(val)
                continue
            elif opt in ('--addr-merge'):
                addr_mask = int(val, 16)
                continue

        self.__addr_merge(searchObj, addr_mask)

        ret = []
        for obj in searchObj:
            entry = []
            for event in keys:
                entry.append(obj[self.__keyword[event]])
            ret.append(entry)
        return ret

    def format(self, info, fmt):
        if (fmt == "raw"):
            return str(info)
        elif (fmt == "data"):
            return info
        else:
            return Monitor.format(self, info, fmt)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: ' + sys.argv[0] + ' fmt path')
        sys.exit(-1)
    ct = PerfTop("UT")
    ct.report(
        sys.argv[1],
        sys.argv[2],
        "--interval=2 --event=cycles;--fields=overhead --fields=symbol --addr-merge=0xffffffffffffffff")
