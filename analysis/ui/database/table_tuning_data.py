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
# Create: 2022-6-25

"""
Func for initial and use tuning_data table.
"""

import re
import logging
import numpy
from sqlalchemy import Table, Column, Integer, VARCHAR
from sqlalchemy.exc import SQLAlchemyError

from analysis.engine.utils import utils

LOGGER = logging.getLogger(__name__)


def initial_table(table_name, metadata, line):
    """initial columns in tuning table"""
    table = Table(table_name, metadata,
                  Column('_round', Integer, primary_key=True),
                  Column('_cost', VARCHAR(255), nullable=False)
                 )
    init_key = '(_round, _cost'
    init_val = '(:_round, :_cost'
    pairs = {'_round': 0, '_cost': 'cost'}
    params = line.split('|')[-2:]
    if len(params) != 2:
        return None, '', '', ''
    for param in params[1].split(','):
        val = param.split('=')[0]
        curr_key = '_' + re.sub(r'[^\w]', '_', val.lower())
        init_key += ', ' + curr_key
        init_val += ', :' + curr_key
        pairs[curr_key] = val
        table.append_column(Column(curr_key, VARCHAR(255), nullable=False))
    for evals in params[0].split(','):
        val = evals.split('=')[0]
        curr_key = '_evaluation_' + re.sub(r'[^\w]', '_', val.lower())
        init_key += ', ' + curr_key
        init_val += ', :' + curr_key
        pairs[curr_key] = 'evaluation-' + val
        table.append_column(Column(curr_key, VARCHAR(255), nullable=False))
    if len(params[0].split(',')) > 1:
        init_key += ', _total_evaluation'
        init_val += ', :_total_evaluation'
        pairs['_total_evaluation'] = 'Total-evaluation'
        table.append_column(Column('_total_evaluation', VARCHAR(255), nullable=False))
    init_key += ')'
    init_val += ')'
    return table, init_key, init_val, pairs


def exist_tuning_column(table, param, session):
    """find column in tuning_data table"""
    key = '_' + re.sub(r'[^\w]', '_', param.lower())
    selects = 'select * from ' + table + ' where \'' + key + '\' is not null'
    try:
        session.execute(selects).fetchall()
    except SQLAlchemyError as err:
        LOGGER.error('Find tuning_data column failed: %s', err)
        return key, False
    return key, True


def execute_tuning_data(table, iteration, line, session):
    """execute data of new round"""
    keys = '(_round, _cost'
    vals = '(:_round, :_cost'
    pairs = {'_round': iteration,
             '_cost': utils.get_time_difference(line.split('|')[2], line.split('|')[1])}
    params = line.split('|')[-2:]
    if len(params) != 2:
        return None, '', ''
    for param in params[1].split(','):
        curr_key, is_col = exist_tuning_column(table, param.split('=')[0], session)
        if is_col:
            keys += ', ' + curr_key
            vals += ', :' + curr_key
            pairs[curr_key] = param.split('=')[1]
    for evals in params[0].split(','):
        curr_key, is_col = exist_tuning_column(table, 'evaluation_' + evals.split('=')[0], session)
        if is_col:
            keys += ', ' + curr_key
            vals += ', :' + curr_key
            pairs[curr_key] = utils.get_opposite_num(evals.split('=')[1], False)
    if len(params[0].split(',')) > 1:
        curr_key, is_col = exist_tuning_column(table, 'total_evaluation', session)
        if is_col:
            keys += ', ' + curr_key
            vals += ', :' + curr_key
            pairs[curr_key] = utils.get_opposite_num(line.split('|')[-3].split('=')[1], True)
    keys += ')'
    vals += ')'
    return keys, vals, pairs


def get_param_by_table_name(table_name, session):
    """get parameter name in table"""
    sql = 'select * from ' + table_name + ' where ' + table_name + '._round = 0'
    res = session.execute(sql).first()
    return [each for each in res][1:]


def get_tuning_data(total_round, table_name, line, session):
    """get tuning data by table_name"""
    end_line = int(line) + 10
    sql = 'select * from ' + table_name + ' where ' + table_name + '._round > ' + \
            str(line) + ' and ' + table_name + '._round <= ' + str(end_line)
    res = session.execute(sql).fetchall()
    lines = len(res) + int(line)
    if lines == total_round:
        lines = -1
    cost = [row[1] for row in res]
    res = [list(row) for row in res]
    res = numpy.array(res).T.tolist()
    return lines, cost, res