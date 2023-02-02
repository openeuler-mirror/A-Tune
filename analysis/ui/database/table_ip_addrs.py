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
Mapping for ip_addrs table.
"""

from sqlalchemy import Column, VARCHAR, Integer, Text, PrimaryKeyConstraint
from sqlalchemy import insert, select, delete, update

from analysis.ui.database.tables import BASE


class IpAddrs(BASE):
    """mapping ip_addrs table"""

    __tablename__ = 'ip_addrs'

    user_id = Column(Integer, nullable=False)
    ip = Column(VARCHAR(255), nullable=False)
    port = Column(VARCHAR(255), nullable=True)
    server_user = Column(VARCHAR(255), nullable=True)
    server_password = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    ip_status = Column(VARCHAR(255), nullable=False, default='rest')

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
    def insert_ip_by_user(ip="", port="", user="", password="", description="", uid=0, session=None):
        """insert ip info into ip_addrs table"""
        sql = insert(IpAddrs).values(user_id=uid, ip=ip, port=port, server_user=user, 
                                        description=description, server_password=password)
        inserts = session.execute(sql)
        return inserts is not None

    @staticmethod
    def update_ip_by_user(ip, port, user, password, description, uid, session):
        """update ip info from ip_addrs table"""
        sql = update(IpAddrs).where(IpAddrs.user_id == uid, IpAddrs.ip == ip) \
                .values(port = port, server_user=user, description=description, 
                        server_password=password)
        res = session.execute(sql)
        return res is not None
    
    @staticmethod
    def delete_ip_by_user(ip, uid, session):
        """delete ip from ip_addrs table"""
        sql = delete(IpAddrs).where(IpAddrs.user_id == uid).where(IpAddrs.ip == ip)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def get_ips_by_uid(uid, session):
        """get all ips by user_id"""
        sql = select([IpAddrs.ip, IpAddrs.description]).where(IpAddrs.user_id == uid)
        tuples = session.execute(sql).fetchall()
        res = []
        for each_line in tuples:
            res.append({'ipAddrs': each_line[0], 'description':  each_line[1]})
        return res

    @staticmethod
    def check_exist_by_ip(ip_addr, uid, session):
        """check if (uid, ip) exist"""
        sql = select([IpAddrs]).where(IpAddrs.user_id == uid).where(IpAddrs.ip == ip_addr)
        return session.execute(sql).scalar() is not None
