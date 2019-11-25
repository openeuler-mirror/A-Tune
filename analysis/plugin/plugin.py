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
The plugin for monitor and configurator.
"""

import sys
import logging
import os
import threading
import monitor
import configurator
import time

logger = logging.getLogger(__name__)


class ThreadedCall(threading.Thread):
    """class for function threaded calling"""

    def __init__(self, func, args=()):
        super(ThreadedCall, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        threading.Thread.join(self)
        try:
            return self.result
        except Exception as err:
            return err


class MPI:
    """The monitor plugin"""

    def __init__(self):
        """
        Initialize.

        :param: None
        :returns: None
        :raises: None
        """
        all_mpis = []
        all_modules = []
        all_purposes = []
        for m in monitor.common.Monitor.__subclasses__():
            all_mpis.append((m._module, m._purpose))
            all_modules.append(m._module)
            all_purposes.append(m._purpose)
        self.get_monitors.__func__.__doc__ = self.get_monitors.__func__.__doc__ % (
            set(all_modules), set(all_purposes))
        self.get_monitor.__func__.__doc__ = self.get_monitor.__func__.__doc__ % (
            all_mpis)

    @classmethod
    def get_monitors(self, module=None, purpose=None):
        """
        Get monitors of 'module' for 'purpose'.

        :param module(optional): %s
        :param purpose(optional): %s
        :returns list: Success, all found monitors or null
        :raises: None
        """
        mpis = []
        for m in monitor.common.Monitor.__subclasses__():
            if (module is not None) and (m._module != module):
                continue
            if (purpose is not None) and (m._purpose != purpose):
                continue
            me = m()
            mpis.append(me)
        return mpis

    @classmethod
    def get_monitor(self, module, purpose):
        """
        Get monitor of 'module' for 'purpose'.

        :param module & purpose: %s
        :returns mpi: Success, the found monitor
        :raises LookupError: Fail, find monitor error
        """
        mpis = MPI.get_monitors(module, purpose)
        if len(mpis) != 1:
            err = LookupError("Find {} {}-{} monitors".format(
                len(mpis), module, purpose))
            logger.error("MPI.{}: {}".format(
                sys._getframe().f_code.co_name, str(err)))
            raise err
        else:
            return mpis[0]

    @classmethod
    def get_monitor_pooled(self, module, purpose, pool):
        """
        Get monitor of 'module' for 'purpose' in pool.

        :param module & purpose: see get_monitor()
        :param pool: monitors pool for looking up
        :returns mpi: Success, the found monitor
        :raises LookupError: Fail, find monitor error
        """
        mpis = []
        for m in pool:
            if (module is not None) and (m._module != module):
                continue
            if (purpose is not None) and (m._purpose != purpose):
                continue
            mpis.append(m)

        if len(mpis) != 1:
            err = LookupError("Find {} {}-{} monitors in pool".format(
                len(mpis), module, purpose))
            logger.error("MPI.{}: {}".format(
                sys._getframe().f_code.co_name, str(err)))
            raise err
        else:
            return mpis[0]

    @classmethod
    def get_monitors_data(self, monitors, pool=None):
        """
        Get given monitors report data in one.

        :param monitors: ((module, purpose, options), ...)
                options is for report(para)
        :param pool: monitors pool for looking up
        :returns list: Success, decoded data strings of all given monitors
        :returns Exceptions: Success, formatted info
        :raises LookupError: Fail, find monitor error
        """
        mts = []
        for m in monitors:
            if pool is None:
                mon = MPI.get_monitor(m[0], m[1])
            else:
                mon = MPI.get_monitor_pooled(m[0], m[1], pool)
            mt = ThreadedCall(mon.report, ("data", None, m[2]))
            mts.append(mt)
            mt.start()

        rets = []
        for mt in mts:
            start = time.time()
            ret = mt.get_result()
            end = time.time()
            logger.debug("MPI.{}: Cost {} s to call {}, ret={}".format(
                sys._getframe().f_code.co_name, end-start, mt.func, str(ret)))
            if isinstance(ret, Exception):
                return ret
            rets += ret
        return rets


class CPI:
    """The configurator plugin"""

    def __init__(self):
        """
        Initialize.

        :param: None
        :returns: None
        :raises: None
        """
        all_cpis = []
        all_modules = []
        all_submods = []
        for m in configurator.common.Configurator.__subclasses__():
            all_cpis.append((m._module, m._submod))
            all_modules.append(m._module)
            all_submods.append(m._submod)
        self.get_configurators.__func__.__doc__ = self.get_configurators.__func__.__doc__ % (
            set(all_modules), set(all_submods))
        self.get_configurator.__func__.__doc__ = self.get_configurator.__func__.__doc__ % (
            all_cpis)

    @classmethod
    def get_configurators(self, module=None, submod=None):
        """
        Get configurators of 'module'.'submod'.

        :param module(optional): %s
        :param submod(optional): %s
        :returns list: Success, all found configurators or null
        :raises: None
        """
        cpis = []
        for c in configurator.common.Configurator.__subclasses__():
            if (module is not None) and (c._module != module):
                continue
            if (submod is not None) and (c._submod != submod):
                continue
            ce = c()
            cpis.append(ce)
        return cpis

    @classmethod
    def get_configurator(self, module, submod):
        """
        Get configurator of 'module'.'submod'.

        :param module & submod: %s
        :returns cpi: Success, the found configurator
        :raises LookupError: Fail, find configurator error
        """
        cpis = CPI.get_configurators(module, submod)
        if len(cpis) != 1:
            err = LookupError("Find {} {}-{} configurators".format(
                len(cpis), module, submod))
            logger.error("CPI.{}: {}".format(
                sys._getframe().f_code.co_name, str(err)))
            raise err
        else:
            return cpis[0]


# if __name__ == "__main__":
#	if len(sys.argv) == 4:
#		ret = MPI.get_monitors(sys.argv[1], sys.argv[2])
#		print(ret[0].get(sys.argv[3]))
#	elif len(sys.argv) == 3:
#		ret = MPI.get_monitors(sys.argv[1], sys.argv[2])
#		print(ret[0].get())
#	else:
#		print('usage: ' + sys.argv[0] + ' module purpose')

# if __name__ == "__main__":
#	if len(sys.argv) == 3:
#		ret = CPI.get_configurators(sys.argv[1])
#		print(ret[0].set(sys.argv[2]))
#	else:
#		print('usage: ' + sys.argv[0] + ' module key=val')

if __name__ == "__main__":
    monitors = (
        ("CPU",
         "STAT",
         "--interval=1;--cpu=1 --fields=usr --fields=sys --fields=iowait --fields=irq --fields=guest"),
        ("STORAGE",
         "STAT",
         "--interval=3;--device=sda --fields=rMBs --fields=wMBs"),
        ("NET",
         "STAT",
         "--interval=2;--nic=lo --fields=wKBs --fields=rKBs"),
        ("PERF",
         "STAT",
         "--interval=5;--fields=cycles --fields=instructions --fields=cache-misses"))
    print(MPI.get_monitors_data(monitors))
