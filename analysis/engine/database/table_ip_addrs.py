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
Mapping for ip_addrs table.
"""

from analysis.engine.database.tables import Base
from sqlalchemy import Column, VARCHAR, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import insert, select

from analysis.engine.database.table_user_account import UserAccount


class IpAddrs(Base):
    """mapping ip_addrs table"""

    __tablename__ = 'ip_addrs'

    user_id = Column(Integer, ForeignKey('user_account.user_id'))
    ip = Column(VARCHAR(255), autoincrement=True, nullable=False)
    ip_status = Column(VARCHAR(255), nullable=False, default='rest')
    fk_user = relationship(UserAccount, backref='ip_addrs')

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'ip', name='pk_ip_addrs'),
    )

    def __repr__(self):
        return "<ip_addrs(ip='%s %s', fk_user='%s')>" % (self.ip, self.ip_status, self.fk_user)

    @staticmethod
    def find_ip(check_ip, session):
        """find check_ip in ip_addrs table"""
        sql = select([IpAddrs]).where(IpAddrs.ip == check_ip)
        res = session.execute(sql).scalar()
        return res is not None

    @staticmethod
    def insert_ip_by_user(iip, uid, session):
        """insert iip and uid into ip_addrs table"""
        sql = insert(IpAddrs).values(user_id=uid, ip=iip)
        inserts = session.execute(sql)
        return inserts is not None

    @staticmethod
    def get_ips_by_uid(uid, session):
        """get all ips by user_id"""
        sql = select([IpAddrs.ip]).where(IpAddrs.user_id == uid)
        tuples = session.execute(sql).fetchall()
        res = []
        for each_line in tuples:
            res.append(each_line[0])
        return res
