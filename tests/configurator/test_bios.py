#!/usr/bin/python3
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
Test case.
"""
from analysis.plugin.configurator.bios.bios import Bios
from analysis.plugin.public import NeedConfigWarning


class TestBios:
    """ test bios"""
    user = "UT"

    def test_get_bios_version(self):
        """test get bios version"""
        try:
            bios = Bios(self.user)
            version = bios.get("version")
            assert version is not None
        except (PermissionError, FileNotFoundError):
            assert True

    def test_is_supported_hpre(self):
        """test whether hpre is supported"""
        try:
            bios = Bios(self.user)
            hpre = bios.get("hpre_support")
            assert hpre is not None
        except (PermissionError, FileNotFoundError):
            assert True

    def test_set_bios_info(self):
        """test set bios info"""
        try:
            bios = Bios(self.user)
            bios.set("version=0.0.0")
            assert False
        except NeedConfigWarning:
            assert True
