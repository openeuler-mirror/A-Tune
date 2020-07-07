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
The sub class of the Configurator, used to change the affinity of irqs.
"""
import inspect
import subprocess
import logging
import os
from analysis.plugin.public import SetConfigError
from ..common import Configurator

LOGGER = logging.getLogger(__name__)


class IrqAffinity(Configurator):
    """To change the affinity of irqs"""
    _module = "AFFINITY"
    _submod = "IRQ"
    _option = "/proc/irq"

    def __init__(self, user=None):
        Configurator.__init__(self, user)
        self._set.__func__.__doc__ = Configurator._set.__doc__ % (
            'irq or irq_name', 'cpumask in hex, no "0x" prefix, "," is permitted')

    @staticmethod
    def __get_irq_id(key):
        if key.isdecimal():
            irq_id = key
            name = None
        else:
            irq_id = None
            name = key

        if irq_id is None:
            irqs = sorted(os.listdir("/sys/kernel/irq/"), key=int)
            for irq in irqs:
                with open("/sys/kernel/irq/{}/actions".format(irq), 'r') as file:
                    action = file.read().replace("\n", "")
                if action == name:
                    irq_id = irq
                    break
        return irq_id

    def _get(self, key, _):
        irq_id = self.__get_irq_id(key)
        if irq_id is None:
            err = LookupError("Fail to find irq {}".format(key))
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err
        with open("{opt}/{id}/smp_affinity".format(opt=self._option, id=irq_id),
                  mode='r',
                  buffering=-1,
                  encoding=None,
                  errors=None,
                  newline=None,
                  closefd=True) as file:
            ret = file.read().replace(",", "")
        return ret

    def _set(self, key, value):
        irq_id = self.__get_irq_id(key)
        if irq_id is None:
            err = LookupError("Fail to find irq {}".format(key))
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))

        mask = value.replace(",", "")
        with open("{opt}/{id}/smp_affinity".format(opt=self._option, id=irq_id), "w") as file:
            ret = subprocess.call(["echo", mask],
                                  shell=False,
                                  stdout=file,
                                  stderr=subprocess.DEVNULL)
        if ret != 0:
            err = SetConfigError("Fail to set irq {} affinity".format(key))
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err
        return ret

    @staticmethod
    def check(config1, config2):
        """replace comma"""
        config1 = config1.replace(",", "")
        config2 = config2.replace(",", "")
        return int(config1, base=16) == int(config2, base=16)
