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
Tool to generate an example of profile configuration.
"""

import sys
sys.path.insert(0, "./../analysis/")
from plugin.plugin import CPI


print("#")
print("# example of atuned profile configuration")
print("#\n")

global_sections = (("main", "list it's parent profile"),
					("tip", "the recommended optimization, which should be performed manunaly"),
					("check", "check the environment"))

for i in global_sections:
	print("[{}]".format(i[0]))
	print("# {}".format(i[1]))
	print("\n")

cpi = CPI()
cpis = cpi.get_configurators()
for i in cpis:
	if i.module() == i.submod():
		print("[{}]".format(i.module().lower()))
	else:
		print("[{}.{}]".format(i.module().lower(), i.submod().lower()))
	print("# {}".format(i.__doc__.lower()))
	print("\n")
