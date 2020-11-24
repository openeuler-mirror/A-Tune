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
Temporary tool to generate the api help info, will be replaced by Sphinx.
"""

from atune_collector.plugin.plugin import CPI, MPI

print("The CPI & MPI api manual")
print("========================\n")

CPI_HELP = CPI()
help(CPI_HELP)

CPIS_HELP = CPI_HELP.get_configurators()
for i in CPIS_HELP:
    help(i)

MPI_HELP = MPI()
help(MPI_HELP)

MPIS_HELP = MPI_HELP.get_monitors()
for i in MPIS_HELP:
    help(i)
