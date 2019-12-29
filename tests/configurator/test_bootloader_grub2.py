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
Test case.
"""
from analysis.plugin.configurator.bootloader.grub2 import Grub2
from analysis.plugin.public import GetConfigError


class TestBootloaderCmdline:
    """ test bootloader grub2"""
    user = "UT"

    def test_get_bootloader_grub2(self):
        """test get bootloader grub2"""
        try:
            grub2 = Grub2(self.user)
            root = grub2.get("root")
            assert root == "UUID"
        except GetConfigError:
            assert True
