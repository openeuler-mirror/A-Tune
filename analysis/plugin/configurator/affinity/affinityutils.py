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
Utils class.
"""

import subprocess
import re


class Utils:
    """Utils class"""

    @staticmethod
    def get_task_id(key):
        """
        get task id
        :param key: the task name or task id
        :returns task_id: converted task id
        """
        if key.isdecimal():
            task_id = key
            name = None
        else:
            task_id = None
            name = key.replace("(", r"\(")
            name = name.replace(")", r"\)")

        if task_id is None:
            output = subprocess.check_output("ps -e".split(),
                                             stderr=subprocess.STDOUT)
            pattern = r"^\ *(\d.*?)\ +.*?\ +.*?\ +" + name
            task_id = re.findall(pattern, output.decode(), re.ASCII | re.MULTILINE)
        return task_id
