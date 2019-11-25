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
The sub class of the monitor, used to collect the CPU stat info.
"""

import sys
import logging
import subprocess
import getopt
import re

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from monitor.common import *

logger = logging.getLogger(__name__)


class CpuStat(Monitor):
    """To collect the CPU stat info"""
    _module = "CPU"
    _purpose = "STAT"
    _option = "-u -P ALL {int} 1"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__cmd = "mpstat"
        self.__interval = 1
        self.format.__func__.__doc__ = Monitor.format.__doc__ % ("json")
        self.decode.__func__.__doc__ = Monitor.decode.__doc__ % (
            "--cpu=n, --fields=time/cpu/usr/nice/sys/iowait/irq/soft/steal/guest/gnice/idle")

    def _get(self, para=None):
        if para is not None:
            opts, args = getopt.getopt(para.split(), None, ['interval='])
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

        output = subprocess.check_output(
            "{cmd} {opt}".format(
                cmd=self.__cmd,
                opt=self._option.format(
                    int=self.__interval)).split())
        return output.decode()

    def format(self, info, fmt):
        if (fmt == "json"):
            o_json = subprocess.check_output(
                "{cmd} -o JSON {opt}".format(
                    cmd=self.__cmd, opt=self._option.format(
                        int=self.__interval)).split())
            return o_json.decode()
        else:
            return Monitor.format(self, info, fmt)

    def decode(self, info, para):
        if para is None:
            return info

        keyword = {"time": 0,
                   "cpu": 1,
                   "usr": 2,
                   "nice": 3,
                   "sys": 4,
                   "iowait": 5,
                   "irq": 6,
                   "soft": 7,
                   "steal": 8,
                   "guest": 9,
                   "gnice": 10,
                   "idle": 11,
                   "cutil": 12}

        keys = []
        cpu = -1    # -1 means all
        threshold = 0
        ret = ""

        opts, args = getopt.getopt(para.split(), None, ['cpu=', 'threshold=', 'fields='])
        for opt, val in opts:
            if opt in ('--cpu'):
                if val.isdigit():
                    cpu = val
                else:
                    err = ValueError("Invalid parameter: {opt}={val}".format(
                        opt=opt, val=val))
                    logger.error(
                        "{}.{}: {}".format(
                            self.__class__.__name__,
                            sys._getframe().f_code.co_name,
                            str(err)))
                    raise err
                continue
            if opt in ('--threshold'):
                try:
                    threshold = float(val)
                except ValueError:
                    err = ValueError("Invalid parameter: {opt}={val}".format(
                        opt=opt, val=val))
                    logger.error(
                        "{}.{}: {}".format(
                            self.__class__.__name__,
                            sys._getframe().f_code.co_name,
                            str(err)))
                    raise err
                continue
            if opt in ('--fields'):
                keys.append(keyword[val])
                continue

        pattern = re.compile(
            "^(\d.*?)\ {2,}(\d*|all)\ {2,}(\d*\.\d*)\ {2,}(\d*\.\d*)\ {2,}(\d*\.\d*)\ {2,}(\d*\.\d*)\ {2,}(\d*\.\d*)\ {2,}(\d*\.\d*)\ {2,}(\d*\.\d*)\ {2,}(\d*\.\d*)\ {2,}(\d*\.\d*)\ {2,}(\d*\.\d*)",
            re.ASCII | re.MULTILINE)
        searchObj = pattern.findall(info)
        if len(searchObj) == 0:
            err = LookupError("Fail to find data for {}".format(cpu))
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err

        stats = []
        for stat in searchObj:
            curr = list(stat)
            curr.append("{:.2f}".format(
                float(stat[keyword["usr"]]) + float(stat[keyword["nice"]]) +
                float(stat[keyword["sys"]]) + float(stat[keyword["irq"]]) +
                float(stat[keyword["soft"]]) + float(stat[keyword["steal"]])))
            stats.append(curr)

        if cpu == -1 and threshold > 0:
            cutil_sum = 0
            cutil_num = 0
            for i in range(1, len(stats)):
                if float(stats[i][keyword["cutil"]]) > threshold:
                    cutil_sum += float(stats[i][keyword["cutil"]])
                    cutil_num += 1
            if cutil_num == 0:
                stats[0][keyword["cutil"]] = "{:.2f}".format(cutil_sum)
            else:
                stats[0][keyword["cutil"]] = "{:.2f}".format(cutil_sum / cutil_num)

        for i in keys:
            ret = ret + " " + stats[cpu+1][i]
        return ret


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: ' + sys.argv[0] + ' fmt path')
        sys.exit(-1)
    ct = CpuStat("UT")
    ct.report(
        sys.argv[1],
        sys.argv[2],
        "--interval=2;--threshold=10.0 --fields=usr --fields=sys --fields=iowait --fields=irq --fields=guest")
