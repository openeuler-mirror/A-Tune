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
from analysis.plugin.configurator.systemctl.systemctl import Systemctl


class TestSystemctl:
    """ test systemctl"""
    user = "UT"
    key = "sshd"

    def test_get_systemctl(self):
        """test get systemctl"""
        systemctl = Systemctl(self.user)
        value = systemctl.get(self.key)
        assert value == ""

    def test_set_systemctl(self):
        """test set systemctl"""
        systemctl = Systemctl(self.user)
        value = systemctl.set("{}=start".format(self.key))
        assert value is not None
