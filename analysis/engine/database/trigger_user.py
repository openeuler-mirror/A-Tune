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
# Create: 2020-12-17

"""
Triggers to action user_account database.
"""

import logging
from sqlalchemy.exc import SQLAlchemyError

from analysis.engine.database import tables
from analysis.engine.database.table_user_account import UserAccount

LOGGER = logging.getLogger(__name__)


def user_exist(email, pwd):
    """check if user exist"""
    session = tables.get_session()
    uid = -1
    account_name = ''
    if session is None:
        return uid, account_name
    try:
        user_account = UserAccount()
        password = user_account.get_field_by_key(UserAccount.password, UserAccount.email, email, session)
        if password is not None and password == pwd:
            uid = user_account.get_field_by_key(UserAccount.user_id, UserAccount.email, email, session)
            account_name = user_account.get_field_by_key(UserAccount.account_name, UserAccount.email, email, session)
    except SQLAlchemyError as err:
        LOGGER.error('User login failed: %s', err)
        return -1, account_name
    finally:
        session.close()
    return uid, account_name


def create_user(email, pwd, name):
    """create new user"""
    session = tables.get_session()
    if session is None:
        return False, False
    try:
        user_account = UserAccount()
        password = user_account.get_field_by_key(UserAccount.password, UserAccount.email, email, session)
        if password is not None:
            return False, True
        uid = user_account.get_max_uid(session) + 1
        user_account.insert_new_user(uid, email, name, pwd, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Create new user failed: %s', err)
        return False, False
    finally:
        session.close()
    return True, False
