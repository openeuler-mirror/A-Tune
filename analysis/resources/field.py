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
Fields used by restful api.
"""

from flask_restful import fields

profile_field = {
    'profile': fields.String,
}

profile_get_field = fields.Nested(profile_field)


param_field = {
    'status': fields.String,
    'value': fields.String,
}

configurator_put_field = fields.Nested(param_field)

optimizer_field = {
    'status': fields.String 
}

optimizer_post_field = {
    'task_id': fields.String
}

classification_field = {
    'resource_limit': fields.String,
    'workload_type': fields.String,
    'percentage': fields.Float,
}

classification_post_field = fields.Nested(classification_field)
