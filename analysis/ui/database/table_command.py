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
# Create: 2023-2-12

"""
Mapping for command_table table.
"""

import time
from sqlalchemy import Column, VARCHAR, Integer, Text
from sqlalchemy import func, select, insert, update

from analysis.ui.database.tables import BASE
from analysis.engine.utils import utils


class CommandTable(BASE):
    """mapping command_table table"""

    __tablename__ = 'command_table'

    command_id = Column(Integer, primary_key=True)
    command_map_id = Column(Integer)
    command_type = Column(VARCHAR(255), nullable=False)
    command_name = Column(VARCHAR(255), nullable=False)
    command_status = Column(VARCHAR(255), nullable=False, default='running')
    command_ip = Column(VARCHAR(255), nullable=False)
    command_date = Column(VARCHAR(255), nullable=False)
    description = Column(Text, default='')

    def __repr__(self):
        return "<command_table(command='%s %s %s %s %s %s %s', description='%s')>" \
                % (self.command_id, self.command_type, self.command_name,
                   self.command_status, self.command_ip, self.command_date,
                   "" if self.description is None else self.description)

    @staticmethod
    def insert_new_command(cid, mid, mtype, name, ip, localtime, session):
        curr_time = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
        sql = insert(CommandTable).values(command_id=cid, command_map_id=mid, command_type=mtype, command_name=name,
                                 command_status='running', command_ip=ip, command_date=curr_time)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def get_max_cid(session):
        """get max tuning_id"""
        sql = func.max(CommandTable.command_id)
        tid = session.query(sql).scalar()
        return 0 if tid is None else tid

    @staticmethod
    def get_field_by_key(field, key, val, session):
        """get field by given key and val pair"""
        sql = select([field]).where(key == val)
        value = session.execute(sql).scalar()
        return value

    @staticmethod
    def get_cid_by_mid_and_type(mid, mtype, session):
        """get command_id by command_map_id and command_type"""
        sql = select([CommandTable.command_id]) \
                     .where(CommandTable.command_map_id == mid) \
                     .where(CommandTable.command_type == mtype)
        value = session.execute(sql).scalar()
        return value

    @staticmethod
    def get_all_command_by_ip(cip, session):
        """get all collections by cip as a list"""
        sql = select([CommandTable.command_name, CommandTable.command_status,
                     CommandTable.command_date, CommandTable.command_ip,
                     CommandTable.description]) \
                     .where(CommandTable.command_ip == cip) \
                     .order_by(CommandTable.command_id.desc())
        res = session.execute(sql).fetchall()
        dicts = ['name', 'status', 'date', 'ip', 'description']
        return utils.zip_key_value(dicts, res)

    @staticmethod
    def get_command_by_ip(ips, page_num, page_size, session):
        """get the page_size data in page_num page with by ips as a list"""
        sql = select([CommandTable.command_id, CommandTable.command_map_id,
                     CommandTable.command_name, CommandTable.command_status, 
                     CommandTable.command_date, CommandTable.command_ip, 
                     CommandTable.command_type, CommandTable.description]) \
                     .where(CommandTable.command_ip.in_(ips)) \
                     .order_by(CommandTable.command_id.desc()) \
                     .limit(page_size).offset((page_num-1)*page_size)
        res = session.execute(sql).fetchall()
        dicts = ['id', 'mid', 'name', 'status', 'date', 'ip', 'type', 'description']
        return utils.zip_key_value(dicts, res)
        
    @staticmethod
    def count_all_command_by_ip(cip, session):
        """count the num of collections by cip"""
        sql = func.count(CommandTable.command_id)
        res = session.query(sql).filter(CommandTable.command_ip==cip).scalar()
        return res

    @staticmethod
    def update_status(cid, status, session):
        """update collection status"""
        sql = update(CommandTable).where(CommandTable.command_map_id == cid) \
                .values(command_status=status)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def update_status_by_name(name, status, session):
        """update collection status"""
        sql = update(CommandTable).where(CommandTable.command_name == name) \
                .values(command_status=status)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def update_name_by_id(cid, name, session):
        """update name"""
        sql = update(CommandTable).where(CommandTable.command_map_id == cid) \
                .values(command_name=name)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def update_description(cid, description, session):
        """update description"""
        sql = update(CommandTable).where(CommandTable.command_id == cid) \
                .values(description=description)
        res = session.execute(sql)
        return res is not None