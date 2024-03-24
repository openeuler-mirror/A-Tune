#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2024-3-23
from flask_caching import Cache


class LocalCache:
    cache = Cache(config={
        "CACHE_TYPE": "simple"
    })

    @staticmethod
    def put(key, value):
        """cache put method"""
        return LocalCache.cache.set(key, value)

    @staticmethod
    def put_with_time(key, value, timeout):
        """cache put method with timeout"""
        return LocalCache.cache.set(key, value, timeout)

    @staticmethod
    def pop(key):
        """cache pop method"""
        return LocalCache.cache.delete(key)

    @staticmethod
    def get(key):
        """cache get method"""
        res = LocalCache.cache.get(key)
        return res
