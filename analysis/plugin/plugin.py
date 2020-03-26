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
The plugin for monitor and configurator.
"""
import inspect
import logging
import threading
import time
from analysis.plugin import monitor
from analysis.plugin import configurator

LOGGER = logging.getLogger(__name__)


class ThreadedCall(threading.Thread):
    """class for function threaded calling"""

    def __init__(self, func, args=()):
        super(ThreadedCall, self).__init__()
        self.func = func
        self.args = args
        self.result = None

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        """start a new thread"""
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
        for sub_class in monitor.common.Monitor.__subclasses__():
            all_mpis.append((sub_class.module(sub_class), sub_class.purpose(sub_class)))
            all_modules.append(sub_class.module(sub_class))
            all_purposes.append(sub_class.purpose(sub_class))
        self.get_monitors.__func__.__doc__ = self.get_monitors.__func__.__doc__ % (
            set(all_modules), set(all_purposes))
        self.get_monitor.__func__.__doc__ = self.get_monitor.__func__.__doc__ % (
            all_mpis)

    @classmethod
    def get_monitors(cls, module=None, purpose=None):
        """
        Get monitors of 'module' for 'purpose'.

        :param module(optional): %s
        :param purpose(optional): %s
        :returns list: Success, all found monitors or null
        :raises: None
        """
        mpis = []
        for sub_class in monitor.common.Monitor.__subclasses__():
            if (module is not None) and (sub_class.module(sub_class) != module):
                continue
            if (purpose is not None) and (sub_class.purpose(sub_class) != purpose):
                continue
            m_class = sub_class()
            mpis.append(m_class)
        return mpis

    @classmethod
    def get_monitor(cls, module, purpose):
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
            LOGGER.error("MPI.%s: %s", inspect.stack()[0][3], str(err))
            raise err
        return mpis[0]

    @classmethod
    def get_monitor_pooled(cls, module, purpose, pool):
        """
        Get monitor of 'module' for 'purpose' in pool.

        :param module & purpose: see get_monitor()
        :param pool: monitors pool for looking up
        :returns mpi: Success, the found monitor
        :raises LookupError: Fail, find monitor error
        """
        mpis = []
        for sub_class in pool:
            if (module is not None) and (sub_class.module() != module):
                continue
            if (purpose is not None) and (sub_class.purpose() != purpose):
                continue
            mpis.append(sub_class)

        if len(mpis) != 1:
            err = LookupError("Find {} {}-{} monitors in pool".format(
                len(mpis), module, purpose))
            LOGGER.error("MPI.%s: %s", inspect.stack()[0][3], str(err))
            raise err
        return mpis[0]

    @classmethod
    def get_monitors_data(cls, monitors, pool=None):
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
        for m_mpi in monitors:
            if pool is None:
                mon = MPI.get_monitor(m_mpi[0], m_mpi[1])
            else:
                mon = MPI.get_monitor_pooled(m_mpi[0], m_mpi[1], pool)
            m_thread = ThreadedCall(mon.report, ("data", None, m_mpi[2]))
            mts.append(m_thread)
            m_thread.start()

        rets = []
        for m_thread in mts:
            start = time.time()
            ret = m_thread.get_result()
            end = time.time()
            LOGGER.debug("MPI.%s: Cost %s s to call %s, ret=%s", inspect.stack()[0][3],
                         end - start, m_thread.func, str(ret))
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
        for sub_class in configurator.common.Configurator.__subclasses__():
            all_cpis.append((sub_class.module(sub_class), sub_class.submod(sub_class)))
            all_modules.append(sub_class.module(sub_class))
            all_submods.append(sub_class.submod(sub_class))
        self.get_configurators.__func__.__doc__ = self.get_configurators.__func__.__doc__ % (
            set(all_modules), set(all_submods))
        self.get_configurator.__func__.__doc__ = self.get_configurator.__func__.__doc__ % (
            all_cpis)

    @classmethod
    def get_configurators(cls, module=None, submod=None):
        """
        Get configurators of 'module'.'submod'.

        :param module(optional): %s
        :param submod(optional): %s
        :returns list: Success, all found configurators or null
        :raises: None
        """
        cpis = []
        for sub_class in configurator.common.Configurator.__subclasses__():
            if (module is not None) and (sub_class.module(sub_class) != module):
                continue
            if (submod is not None) and (sub_class.submod(sub_class) != submod):
                continue
            c_cpi = sub_class()
            cpis.append(c_cpi)
        return cpis

    @classmethod
    def get_configurator(cls, module, submod):
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
            LOGGER.error("CPI.%s: %s", inspect.stack()[0][3], str(err))
            raise err
        return cpis[0]
