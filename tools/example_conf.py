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
Tool to generate an example of profile configuration.
"""

from atune_collector.plugin.plugin import CPI

print("#")
print("# example of atuned profile configuration")
print("#\n")

GLOBAL_SECTIONS = (("main", "list it's parent profile"),
                   ("tip", "the recommended optimization, which should be performed manunaly"),
                   ("check", "check the environment"))

for i in GLOBAL_SECTIONS:
    print(f"[{i[0]}]")
    print(f"# {i[1]}")
    print("\n")

CPI_INSTANCE = CPI()
CPIS = CPI_INSTANCE.get_configurators()
for i in CPIS:
    if i.module() == i.submod():
        print(f"[{i.module().lower()}]")
    else:
        print(f"[{i.module().lower()}.{i.submod().lower()}]")
    print(f"# {i.__doc__.lower()}")
    print("\n")
