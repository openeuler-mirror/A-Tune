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
from analysis.plugin.configurator.affinity.processid import ProcessidAffinity


class TestAffinityProcessid:
    """ test affinity processid"""
    user = "UT"

    def test_get_affinity_pid_sshd(self):
        """test get affinity processid about sshd"""
        processid_affinity = ProcessidAffinity(self.user)
        processid = processid_affinity.get("sshd")
        assert processid is not None

    def test_get_affinity_pid_atune(self):
        """test get affinity processid about atune"""
        try:
            processid_affinity = ProcessidAffinity(self.user)
            processid_affinity.get("atune")
            assert False
        except LookupError:
            assert True
