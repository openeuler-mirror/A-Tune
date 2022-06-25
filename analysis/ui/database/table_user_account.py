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
Mapping for user_account table.
"""

from sqlalchemy import Column, VARCHAR, Integer, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy import func, select, insert, update, delete

from analysis.ui.database.tables import BASE


class UserAccount(BASE):
    """mapping user_account table"""

    __tablename__ = 'user_account'

    user_id = Column(Integer, autoincrement=True, primary_key=True)
    account_name = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(255), nullable=False, unique=True)
    password = Column(VARCHAR(255), nullable=False)
    role = Column(VARCHAR(255), nullable=False, default='user')

    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='pk_users'),
        UniqueConstraint('email', name='uk_email')
    )

    def __repr__(self):
        return "<user_account(user_id='%s', info='%s %s', limitaion='%s')>" % \
                (self.user_id, self.account_name, self.email,self.limitation)

    @staticmethod
    def find_user(uid, session):
        """find uid in user_account table"""
        sql = select([UserAccount]).where(UserAccount.user_id == uid)
        res = session.execute(sql).scalar()
        return res is not None

    @staticmethod
    def get_field_by_key(field, key, val, session):
        """get user password by email"""
        sql = select([field]).where(key == val)
        res = session.execute(sql).scalar()
        return res

    @staticmethod
    def get_max_uid(session):
        """get max user_id in user_account table"""
        sql = func.max(UserAccount.user_id)
        uid = session.query(sql).scalar()
        return uid

    @staticmethod
    def insert_new_user(uid, email, name, pwd, session, role='user'):
        """insert new user into user_account table"""
        sql = insert(UserAccount).values(user_id=uid, account_name=name, email=email,
                                         password=pwd, role=role)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def update_password(uid, pwd, session):
        """update password"""
        sql = update(UserAccount).where(UserAccount.user_id == uid).values(password=pwd)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def delete_user(uid, session):
        """update user by id"""
        sql = delete(UserAccount).where(UserAccount.user_id == uid)
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def find_all_user(session):
        """find uid in user_account table"""
        sql = select([UserAccount])
        res = session.execute(sql).scalar()
        return res is not None

    @staticmethod
    def update_user(uid, pwd, name, role, session):
        """update user details"""
        sql = update(UserAccount).where(UserAccount.user_id == uid).values(account_name=name,
                                                                           password=pwd, role=role)
        res = session.execute(sql)
        return res is not None
