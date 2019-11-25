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
Used to create tasks for optimizer.
"""


class TasksCache(object):
    tasks = {}

    #以下类方法，用于单例模式
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(TasksCache, cls).__new__(cls, *args, **kwargs)
            return cls.__instance

    @classmethod
    def getInstance(cls):
        if(cls.__instance is None):
            cls.__instance = TasksCache()
        return cls.__instance

    def get(self, key, default=None):
        return self.tasks.get(key) if key in self.tasks.keys() else None

    def set(self, key, value):
        self.tasks[key] = value

    def delete(self, key):
        del self.tasks[key]

    def get_all(self):
        return self.tasks
