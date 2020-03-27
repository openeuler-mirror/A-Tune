#!/usr/bin/env python3
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
The sub class of the monitor, used to collect the perf top snapshot.
"""
import inspect
import logging
import os
import subprocess
import getopt
import re
import random
from ..common import Monitor

LOGGER = logging.getLogger(__name__)


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
        for word in self.__keyword:
            help_info = help_info + word + "/"
        help_info = help_info.strip("/")
        self.decode.__func__.__doc__ = Monitor.decode.__doc__ % (help_info)

    def _get(self, para=None):
        if para is not None:
            opts, _ = getopt.getopt(
                para.split(), None, [
                    'interval=', 'event='])
            for opt, val in opts:
                if opt in '--interval':
                    if val.isdigit():
                        self.__interval = int(val)
                    else:
                        err = ValueError(
                            "Invalid parameter: {opt}={val}".format(
                                opt=opt, val=val))
                        LOGGER.error("%s.%s: %s", self.__class__.__name__,
                                     inspect.stack()[0][3], str(err))
                        raise err
                    continue
                if opt in '--event':
                    self.__event = val.split(",")[-1]
                    continue

        data_file = "/run/atuned/perf{}".format(random.random())
        data_path = os.path.dirname(data_file.strip())
        if not os.path.exists(data_path):
            os.makedirs(data_path, 0o750)
        subprocess.check_output(
            "perf record -o {data} {opt}".format(
                opt=self._option.format(
                    event=self.__event,
                    int=self.__interval),
                data=data_file).split(),
            stderr=subprocess.DEVNULL)
        output = subprocess.check_output("perf report --stdio -i {data}".format(
            data=data_file).split(), stderr=subprocess.STDOUT)
        return output.decode()

    def __add_merge_entry(self, merge, entry, mask):
        entry = list(entry)
        entry[self.__keyword["overhead"]] = float(
            entry[self.__keyword["overhead"]])
        entry[self.__keyword["symbol"]] = int(
            entry[self.__keyword["symbol"]], 16)

        for i, _ in enumerate(merge):
            if (merge[i][self.__keyword["command"]] == entry[self.__keyword["command"]]) and (
                    merge[i][self.__keyword["object"]] == entry[self.__keyword["object"]]):
                entry_addr = entry[self.__keyword["symbol"]] & ~mask
                merged_addr = merge[i][self.__keyword["symbol"]] & ~mask
                if entry_addr == merged_addr:
                    merge[i][self.__keyword["overhead"]] += entry[self.__keyword["overhead"]]
                    merge[i][self.__keyword["symbol"]] = merged_addr
                    return

        merge.append(entry)

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

        for i, _ in enumerate(merge):
            merge[i][self.__keyword["overhead"]] = "%2.2f" % merge[i][self.__keyword["overhead"]]
            merge[i][self.__keyword["symbol"]] = "0x%016x" % merge[i][self.__keyword["symbol"]]
            info.append(merge[i])

    def decode(self, info, para):
        """
        decode the result of the operation
        :param info:  content that needs to be decoded
        :param para:  command line argument
        :returns ret:  operation result
        """
        if para is None:
            return info

        pattern = re.compile(
            r"^\ {2,}(\d.*?)%\ {2,}(\w.*?)\ {1,}(.*?)\ {2,}\[[.|k]\]\ (\w.*)",
            re.ASCII | re.MULTILINE)
        search_obj = pattern.findall(info)
        if len(search_obj) == 0:
            err = LookupError("Fail to find data")
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err

        keys = []
        opts, _ = getopt.getopt(
            para.split(), None, [
                'fields=', 'addr-merge='])
        for opt, val in opts:
            if opt in '--fields':
                keys.append(val)
                continue
            if opt in '--addr-merge':
                addr_mask = int(val, 16)
                continue

        self.__addr_merge(search_obj, addr_mask)

        ret = []
        for obj in search_obj:
            entry = []
            for event in keys:
                entry.append(obj[self.__keyword[event]])
            ret.append(entry)
        return ret

    def format(self, info, fmt):
        """
        format the result of the operation
        :param info:  content that needs to be converted
        :param fmt:  converted format
        """
        if fmt == "raw":
            return str(info)
        if fmt == "data":
            return info
        return Monitor.format(self, info, fmt)
