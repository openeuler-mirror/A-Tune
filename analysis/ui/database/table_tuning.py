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
# Create: 2020-12-04

"""
Mapping for tuning_table table.
"""

import time
from sqlalchemy import Column, VARCHAR, Integer
from sqlalchemy import func, select, insert, update

from analysis.ui.database.tables import BASE
from analysis.engine.utils import utils


class TuningTable(BASE):
    """mapping tuning_table table"""

    __tablename__ = 'tuning_table'

    tuning_id = Column(Integer, autoincrement=True, primary_key=True)
    tuning_name = Column(VARCHAR(255), nullable=False)
    tuning_engine = Column(VARCHAR(255), nullable=True)
    tuning_status = Column(VARCHAR(255), nullable=False, default='running')
    tuning_ip = Column(VARCHAR(255), nullable=False)
    tuning_date = Column(VARCHAR(255), nullable=False)
    total_round = Column(Integer, nullable=True)
    baseline = Column(VARCHAR(255))

    def __repr__(self):
        return "<tuning_table(tuning='%s %s %s %s %s %s', round='%s', baseline='%s')>" \
                % (self.tuning_id, self.tuning_name, self.tuning_engine,
                   self.tuning_status, self.tuning_date, self.tuning_ip,
                   0 if self.total_round is None else self.total_round,
                   0 if self.baseline is None else self.baseline)


    @staticmethod
    def insert_new_tuning(tid, name, engine, rounds, tip, session):
        """insert new tuning into tuning_table"""
        curr_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = ''
        if rounds != '0':
            sql = insert(TuningTable).values(tuning_id=tid, tuning_name=name,
                         tuning_engine=engine, total_round=int(rounds), tuning_status='running',
                         tuning_ip=tip, tuning_date=curr_time)
        else:
            sql = insert(TuningTable).values(tuning_id=tid, tuning_name=name,
                         tuning_engine=engine, tuning_status='running', tuning_ip=tip,
                         tuning_date=curr_time)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def check_exist_by_name(field, name, session):
        """check if tuning exist"""
        sql = select([field]).where(TuningTable.tuning_name == name)
        res = session.execute(sql).fetchall()
        return len(res) != 0

    @staticmethod
    def get_max_tid(session):
        """get max tuning_id"""
        sql = func.max(TuningTable.tuning_id)
        tid = session.query(sql).scalar()
        return 0 if tid is None else tid

    @staticmethod
    def get_field_by_name(field, name, session):
        """get field info by name"""
        sql = select([field]).where(TuningTable.tuning_name == name)
        value = session.execute(sql).scalar()
        return value

    @staticmethod
    def get_all_tunings_by_ip(tip, session):
        """get all tunings by tip as a list"""
        sql = select([TuningTable.tuning_name, TuningTable.tuning_status, TuningTable.tuning_date,
                     TuningTable.tuning_ip]).where(TuningTable.tuning_ip == tip) \
                     .order_by(TuningTable.tuning_id.desc())
        res = session.execute(sql).fetchall()
        dicts = ['name', 'status', 'date', 'info']
        return utils.zip_key_value(dicts, res)

    @staticmethod
    def get_status_tuning_by_ip(status, tip, session):
        """get tunings in given status by tip as a list"""
        sql = select([TuningTable.tuning_name, TuningTable.tuning_status, TuningTable.tuning_date,
                     TuningTable.tuning_ip]).where(TuningTable.tuning_ip == tip) \
                     .where(TuningTable.tuning_status == status) \
                     .order_by(TuningTable.tuning_id.desc())
        res = session.execute(sql).fetchall()
        dicts=['name', 'status', 'date', 'info']
        return utils.zip_key_value(dicts, res)

    @staticmethod
    def update_baseline(name, base, session):
        """update baseline by tuning_name"""
        sql = update(TuningTable).where(TuningTable.tuning_name == name).values(baseline=base)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def update_status(name, status, session):
        """update status"""
        sql = update(TuningTable).where(TuningTable.tuning_name == name) \
                .values(tuning_status=status)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def update_tuning_name(name, new_name, session):
        """update tuning name"""
        sql = update(TuningTable).where(TuningTable.tuning_name == name) \
                .values(tuning_name=new_name)
        res = session.execute(sql)
        return res is not None