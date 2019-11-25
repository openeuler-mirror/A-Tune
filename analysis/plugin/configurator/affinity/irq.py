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
The sub class of the Configurator, used to change the affinity of irqs.
"""

import sys
import logging
import os

if __name__ == "__main__":
    sys.path.insert(0, "./../../")
from configurator.common import *

logger = logging.getLogger(__name__)


class IrqAffinity(Configurator):
    """To change the affinity of irqs"""
    _module = "AFFINITY"
    _submod = "IRQ"
    _option = "/proc/irq"

    def __init__(self, user=None):
        Configurator.__init__(self, user)
        self._set.__func__.__doc__ = Configurator._set.__doc__ % (
            'irq or irq_name', 'cpumask in hex, no "0x" prefix, "," is permitted')

    def __get_irq_id(self, key):
        if key.isdecimal():
            id = key
            name = None
        else:
            id = None
            name = key

        if id is None:
            irqs = sorted(os.listdir("/sys/kernel/irq/"), key=lambda x: int(x))
            for irq in irqs:
                with open("/sys/kernel/irq/{}/actions".format(irq), 'r') as f:
                    action = f.read().replace("\n", "")
                if action == name:
                    id = irq
                    break
        return id

    def _get(self, key):
        id = self.__get_irq_id(key)
        if id is None:
            err = LookupError("Fail to find irq {}".format(key))
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err

        f = open("{opt}/{id}/smp_affinity".format(opt=self._option,
                                                  id=id),
                 mode='r',
                 buffering=-1,
                 encoding=None,
                 errors=None,
                 newline=None,
                 closefd=True)
        ret = f.read().replace(",", "")
        f.close()
        return ret

    def _set(self, key, value):
        id = self.__get_irq_id(key)
        if id is None:
            err = LookupError("Fail to find irq {}".format(key))
            logger.error(
                "{}.{}: {}".format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name,
                    str(err)))
            raise err

        mask = value.replace(",", "")
        f = open("{opt}/{id}/smp_affinity".format(opt=self._option,
                                                  id=id),
                 mode='w',
                 buffering=-1,
                 encoding=None,
                 errors=None,
                 newline=None,
                 closefd=True)
        f.write(mask)
        f.close()
        return 0

    def _check(self, config1, config2):
        config1 = config1.replace(",", "")
        config2 = config2.replace(",", "")
        return int(config1, base=16) == int(config2, base=16)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: ' + sys.argv[0] + ' key=value')
        sys.exit(-1)
    ct = IrqAffinity("UT")
    print(ct.set(sys.argv[1]))
    print(ct.get(ct._getcfg(sys.argv[1])[0]))
