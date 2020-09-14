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
Init file.
"""
import os
import sys

sys.path.append("../../")

import test_affinity_irq

affinityirq = test_affinity_irq.TestAffinityIrq()
affinityirq.test_get_affinity_irq_with_none()
affinityirq.test_set_affinity_irq_with_none()


import test_affinity_processid

affinityid = test_affinity_processid.TestAffinityProcessid()
affinityid.test_get_affinity_pid_sshd()
affinityid.test_get_affinity_pid_atune()


import test_affinity_task

affinitytask = test_affinity_task.TestAffinityTask()
affinitytask.test_get_affinity_task()


import test_bios

bios = test_bios.TestBios()
bios.test_get_bios_version()
bios.test_is_supported_hpre()
bios.test_set_bios_info()


import test_bootloader_cmdline

bootloadercmd = test_bootloader_cmdline.TestBootloaderCmdline()
bootloadercmd.test_get_bootloader_cmdline()


import test_bootloader_grub2

bootloadergrub2 = test_bootloader_grub2.TestBootloaderCmdline()
bootloadergrub2.test_get_bootloader_grub2()


import test_kernel_config

kernelcnf = test_kernel_config.TestKernelConfig()
kernelcnf.test_get_kernel_config_no_exist()
kernelcnf.test_get_kernel_config()
kernelcnf.test_set_kernel_config_active()
kernelcnf.test_set_kernel_config()


import test_script

script = test_script.TestScript()
script.test_get_script_with_hugepage()


import test_sysctl

sysctl = test_sysctl.TestSysctl()
sysctl.test_get_sysctl()


import test_sysfs

sysfs = test_sysfs.TestSysfs()
sysfs.test_get_sysctl()


import test_systemctl

systemctl = test_systemctl.TestSystemctl()
systemctl.test_get_systemctl()
systemctl.test_set_systemctl()


import test_ulimit

ulimit = test_ulimit.TestUlimit()
ulimit.test_get_ulimit()
