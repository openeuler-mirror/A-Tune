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
from analysis.plugin.configurator.affinity.irq import IrqAffinity


class TestAffinityIrq:
    """ test affinity irq"""
    user = "UT"
    actions_info_not_exist = "test_affinity_irq_no_exist"
    affinity_info_modify = "3"

    def test_get_affinity_irq_with_none(self):
        """test get affinity irq whith none"""
        try:
            irq_affinity = IrqAffinity(self.user)
            irq_affinity.get(self.actions_info_not_exist)
            assert False
        except LookupError:
            assert True

    def test_set_affinity_irq_with_none(self):
        """test set affinity irq whith none"""
        try:
            irq_affinity = IrqAffinity(self.user)
            irq_affinity.set("{}={}".format(self.actions_info_not_exist, self.affinity_info_modify))
            assert False
        except FileNotFoundError:
            assert True
