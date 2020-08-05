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
import subprocess

from analysis.plugin.configurator.affinity.task import TaskAffinity
from analysis.plugin.configurator.affinity.affinityutils import Utils


class TestAffinityTask:
    """ test affinity task"""
    user = "UT"
    process_name = "rsyslogd"
    cpuinfo = "/proc/cpuinfo"

    def test_get_affinity_task(self):
        """test get affinity task"""
        task_affinity = TaskAffinity(self.user)
        tasks = Utils.get_task_id(self.process_name)
        if tasks is None:
            raise LookupError("Fail to find task {}".format(self.process_name))
        affinity_mask = task_affinity.get(tasks[0])
        out_cat = subprocess.Popen(["cat", self.cpuinfo], stdout=subprocess.PIPE, shell=False)
        out_grep = subprocess.Popen(["grep", "processor"], stdin=out_cat.stdout,
                                    stdout=subprocess.PIPE, shell=False)
        out_wc = subprocess.Popen(["wc", "-l"], stdin=out_grep.stdout, stdout=subprocess.PIPE,
                                  shell=False)
        output = out_wc.communicate()
        count = int(bytes.decode(output[0]).strip()) >> 2
        assert affinity_mask == count * 'f'
