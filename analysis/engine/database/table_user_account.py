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
Mapping for user_account table.
"""

from analysis.engine.database.tables import Base
from sqlalchemy import Column, VARCHAR, Integer, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy import select


class UserAccount(Base):
    """mapping user_account table"""

    __tablename__ = 'user_account'

    user_id = Column(Integer, autoincrement=True, primary_key=True)
    account_name = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(255), nullable=False, unique=True)
    password = Column(VARCHAR(255), nullable=False)
    limitation = Column(VARCHAR(255), nullable=False, default='user')

    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='pk_users'),
        UniqueConstraint('email', name='uk_email')
    )

    def __repr__(self):
        return "<user_account(user_id='%s', info='%s %s', limitaion='%s')>" % (self.user_id,
                self.account_name, self.email, self.limitation)

    @staticmethod
    def find_user(uid, session):
        """find uid in user_account table"""
        sql = select([UserAccount]).where(UserAccount.user_id == uid)
        res = session.execute(sql).scalar()
        return res is not None
