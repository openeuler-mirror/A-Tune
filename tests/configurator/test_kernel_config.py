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
Test case.
"""
from analysis.plugin.configurator.kernel_config.kconfig import KernelConfig
from analysis.plugin.public import NeedConfigWarning


class TestKernelConfig:
    """ test kernel config"""
    user = "UT"
    config_key = "CONFIG_EULEROS_DETAILED_RAS_INFO"

    def test_get_kernel_config_no_exist(self):
        """test get kernel config with no exist"""
        try:
            kernel_config = KernelConfig(self.user)
            value = kernel_config.get("CONFIG_EULEROS_TEST_KERNEL_CONFIG")
            assert value is None
        except (FileNotFoundError, LookupError):
            assert True

    def test_get_kernel_config(self):
        """test get kernel config"""
        try:
            kernel_config = KernelConfig(self.user)
            value = kernel_config.get(self.config_key)
            assert value == "y"
        except FileNotFoundError:
            assert True

    def test_set_kernel_config_active(self):
        """test get kernel config"""
        try:
            kernel_config = KernelConfig(self.user)
            value = kernel_config.set("{}=y".format(self.config_key))
            assert value is None
        except (FileNotFoundError, NeedConfigWarning):
            assert True

    def test_set_kernel_config(self):
        """test get kernel config"""
        try:
            kernel_config = KernelConfig(self.user)
            kernel_config.set("{}=n".format(self.config_key))
            assert False
        except (FileNotFoundError, NeedConfigWarning):
            assert True

