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
The sub class of the Configurator, used to get process id.
"""
import inspect
import logging

from .affinityutils import Utils
from ..common import Configurator

LOGGER = logging.getLogger(__name__)


class ProcessidAffinity(Configurator):
    """To get process id"""
    _module = "AFFINITY"
    _submod = "PROCESSID"

    def __init__(self, user=None):
        Configurator.__init__(self, user)

    def _get(self, key, _):
        task_id = Utils.get_task_id(key)
        task_id = " ".join(task_id)
        if task_id == "":
            err = LookupError("Fail to find process {}".format(key))
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err
        return task_id
