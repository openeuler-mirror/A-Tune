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
Mapping for collection_table table.
"""

import time
from sqlalchemy import Column, VARCHAR, Integer
from sqlalchemy import func, select, insert, update

from analysis.ui.database.tables import BASE
from analysis.engine.utils import utils


class CollectionTable(BASE):
    """mapping collection_table table"""

    __tablename__ = 'collection_table'

    collection_id = Column(Integer, primary_key=True)
    collection_name = Column(VARCHAR(255), nullable=False)
    collection_status = Column(VARCHAR(255), nullable=False, default='running')
    collection_ip = Column(VARCHAR(255), nullable=False)
    collection_date = Column(VARCHAR(255), nullable=False)
    workload_type = Column(VARCHAR(255), nullable=True)
    total_round = Column(Integer)
    total_log = Column(Integer)

    def __repr__(self):
        return "<collection_table(collection='%s %s %s %s %s', round='%s %s')>" \
                % (self.collection_id, self.collection_name, self.collection_status,
                   self.collection_date, self.collection_ip,
                   0 if self.total_round is None else self.total_round,
                   0 if self.total_log is None else self.total_log)

    @staticmethod
    def insert_new_collection(cid, cip, session):
        """insert new collection to collection_table"""
        localtime = time.localtime()
        times = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
        name = int(time.mktime(localtime))
        sql = insert(CollectionTable).values(collection_id=cid, collection_status='running',
                     collection_ip=cip, collection_date=times, collection_name=str(name))
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def check_exist_by_name(field, name, session):
        """find field if exist"""
        sql = select([field]).where(CollectionTable.collection_name == name)
        res = session.execute(sql).fetchall()
        return len(res) != 0

    @staticmethod
    def get_max_cid(session):
        """get max collection_id in collection_table"""
        sql = func.max(CollectionTable.collection_id)
        cid = session.query(sql).scalar()
        if cid is None or cid == -1:
            cid = 0
        return cid

    @staticmethod
    def get_field_by_key(field, key, val, session):
        """get field by given key and val pair"""
        sql = select([field]).where(key == val)
        value = session.execute(sql).scalar()
        return value

    @staticmethod
    def get_all_collection_by_ip(cip, session):
        """get all collections by cip as a list"""
        sql = select([CollectionTable.collection_name, CollectionTable.collection_status,
                     CollectionTable.collection_date, CollectionTable.collection_ip]) \
                     .where(CollectionTable.collection_ip == cip) \
                     .order_by(CollectionTable.collection_id.desc())
        res = session.execute(sql).fetchall()
        dicts = ['name', 'status', 'date', 'info']
        return utils.zip_key_value(dicts, res)

    @staticmethod
    def update_status(cid, status, session):
        """update collection status"""
        sql = update(CollectionTable).where(CollectionTable.collection_id == cid) \
                .values(collection_status=status)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def update_total_round(cid, rounds, session):
        """update total round"""
        update_round = update(CollectionTable) \
                .where(CollectionTable.collection_id == cid) \
                .values(total_round=rounds)
        res = session.execute(update_round)
        return res is not None

    @staticmethod
    def update_collection_name(name, new_name, session):
        """update name by name"""
        sql = update(CollectionTable).where(CollectionTable.collection_name == name) \
                .values(collection_name=new_name)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def update_total_log(cid, logs, session):
        """update total log"""
        update_log = update(CollectionTable) \
                .where(CollectionTable.collection_id == cid) \
                .values(total_log=logs)
        res = session.execute(update_log)
        return res is not None

    @staticmethod
    def update_name(cid, name, session):
        """update name"""
        sql = update(CollectionTable).where(CollectionTable.collection_id == cid) \
                .values(collection_name=name)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def update_workload(cid, workload, session):
        """update workload"""
        sql = update(CollectionTable).where(CollectionTable.collection_id == cid) \
                .values(workload_type=workload)
        res = session.execute(sql)
        return res is not None
