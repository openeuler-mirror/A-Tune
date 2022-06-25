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
Mapping for collection_data table.
"""

import re
import numpy
from sqlalchemy import MetaData, create_engine
from sqlalchemy import Table, Column, VARCHAR, Integer
from sqlalchemy import text
from sqlalchemy.engine.reflection import Inspector

from analysis.ui.database.tables import get_db_url


def exists_table(table_name):
    """check if table exists"""
    engine = create_engine(get_db_url())
    inspector = Inspector.from_engine(engine)
    table = inspector.get_table_names()
    return table_name in table


def initial_table(table_name, session):
    """initial collection data table"""
    metadata = MetaData()
    table = Table(table_name, metadata,
                  Column('collection_id', Integer, primary_key=True, nullable=False),
                  Column('round', Integer, primary_key=True, nullable=False),
                  Column('timestamp', VARCHAR(255), nullable=True)
                 )
    engine = create_engine(get_db_url())
    metadata.create_all(engine)
    sql = 'insert into ' + table_name + ' values (-1, -1, \'timeStamp\')'
    session.execute(sql)
    return table


def get_max_round(cid, cip, session):
    """get max round num in collection_table"""
    table_name = get_table_name(cip)
    if table_name is None:
        return False
    if not exists_table(table_name):
        initial_table(table_name, session)
    sql = 'select max(round) from ' + table_name + ' where collection_id = :id'
    cid = session.execute(text(sql), {'id': cid}).scalar()
    if cid is None or cid == -1:
        return 0
    return cid


def insert_table(cid, rounds, cip, data, session):
    """insert data into collection_ip table"""
    table_name = get_table_name(cip)
    if table_name is None:
        return False
    keys, vals, pairs = execute_collection_data(cid, rounds, data, table_name, session)
    sql = 'insert into ' + table_name + ' ' + keys + ' values ' + vals
    session.execute(text(sql), pairs)
    return True


def execute_collection_data(cid, rounds, data, table_name, session):
    """execute data of new round"""
    keys = '(collection_id, round'
    vals = '(:collection_id, :round'
    pairs = {'collection_id': cid, 'round': rounds}
    for element in data.split(' '):
        param = element.split(':')
        col_name = re.sub(r'[^\w]', '_', param[0].lower())
        if len(param) != 2:
            continue
        if not exist_column(table_name, col_name, session):
            insert_new_column(table_name, col_name, param[0], session)
        keys += ', ' + col_name
        vals += ', :' + col_name
        pairs[col_name] = param[1]
    keys += ')'
    vals += ')'
    return keys, vals, pairs


def exist_column(table_name, col_name, session):
    """find if column col_name exist"""
    sql = 'select * from ' + table_name + ' where collection_id = -1'
    res = session.execute(sql).fetchall()[0]
    return col_name in tuple(res)


def insert_new_column(table_name, col_name, param, session):
    """insert new column to collection_data table"""
    sql = 'alter table ' + table_name + ' add column if not exists ' + col_name + \
        ' varchar(255) default null'
    session.execute(sql)
    update_sql = 'update ' + table_name + ' set ' + col_name + ' = :param where collection_id = -1'
    session.execute(text(update_sql), {'param': param})


def get_table_name(ip):
    """get collection data table name by ip"""
    if ip is None or ip == '':
        return ip
    return 'collection_' + re.sub(r'[^\w]', '_', ip.lower())


def get_line(cip, cid, start, end, session):
    """get selected line by cid and line range, return data & round"""
    table_name = get_table_name(cip)
    sql = 'select * from ' + table_name + \
        ' where collection_id = :id and round > :round1 and round <= :round2'
    res = session.execute(text(sql), {'id': cid, 'round1': start, 'round2': end}).fetchall()
    if len(res) == 0:
        return [], []
    if cid == -1:
        return list(res[0])[2:], [] # get param name
    rounds = [row[1] for row in res]
    res = [list(row)[2:] for row in res]
    res = numpy.array(res).T.tolist()
    return res, rounds