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
Load a parser from its name.
"""

import parser.base

_NAMESPASE = "parser"
_PREFIX = ""
_SUFFIX = "_parser"
_INTERFACE = parser.base.Parser

def load_parser(parser_name):
    """load a parser from its name.

    @param parser_name: the name of the parser to load
    @return: class of the parser to load
    """
    module_name = "{}.{}{}{}".format(_NAMESPASE, _PREFIX, parser_name.replace("-", "_"), _SUFFIX)
    module = __import__(module_name)
    path = module_name.split(".")
    path.pop(0)

    while path:
        module = getattr(module, path.pop(0))

    for name in dir(module):
        cls = getattr(module, name)
        if issubclass(cls, _INTERFACE):
            return cls

    return ImportError("Can not find the parser class")
