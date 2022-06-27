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
Triggers to action user_account database.
"""

import logging
from sqlalchemy.exc import SQLAlchemyError

from analysis.ui.database import tables
from analysis.ui.database.table_user_account import UserAccount
from analysis.ui.database.table_ip_addrs import IpAddrs
from analysis.ui.database.table_tuning import TuningTable
from analysis.ui.database.table_collection import CollectionTable

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
        password = user_account.get_field_by_key(UserAccount.password, UserAccount.email, email,
                                                 session)
        if password is not None and password == pwd:
            uid = user_account.get_field_by_key(UserAccount.user_id, UserAccount.email, email,
                                                session)
            account_name = user_account.get_field_by_key(UserAccount.account_name,
                                                         UserAccount.email, email, session)
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
        password = user_account.get_field_by_key(UserAccount.password, UserAccount.email, email,
                                                 session)
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


def user_ip_list(uid):
    """get all ip as list for given user"""
    session = tables.get_session()
    res = []
    if session is None:
        return res
    try:
        ip_table = IpAddrs()
        res.extend(ip_table.get_ips_by_uid(uid, session))
    except SQLAlchemyError as err:
        LOGGER.error('Get user ip list failed: %s', err)
        return []
    finally:
        session.close()
    return res


def ip_info_list(ip_addr):
    """get analysis and tuning list with ip_addr"""
    session = tables.get_session()
    if session is None:
        return {'getData': False}
    response = {}
    try:
        response['getData'] = True
        tuning_table = TuningTable()
        response['tuning'] = tuning_table.get_all_tunings_by_ip(ip_addr, session)
        collection_table = CollectionTable()
        response['analysis'] = collection_table.get_all_collection_by_ip(ip_addr, session)
    except SQLAlchemyError as err:
        LOGGER.error('Get analysis and tuning list failed: %s', err)
        return response
    finally:
        session.close()
    return response


def add_ip(uid, ip_addrs):
    """add ip to table"""
    session = tables.get_session()
    if session is None:
        return False
    res = False
    try:
        ip_table = IpAddrs()
        if not ip_table.check_exist_by_ip(ip_addrs, uid, session):
            res = ip_table.insert_ip_by_user(ip_addrs, uid, session)
            session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Insert new ip failed: %s', err)
        return res
    finally:
        session.close()
    return res


def change_user_pwd(uid, pwd, new_pwd):
    """check if user password match pwd"""
    session = tables.get_session()
    if session is None:
        return {'oldMatch': False}
    response = {}
    try:
        user_account = UserAccount()
        password = user_account.get_field_by_key(UserAccount.password, UserAccount.user_id, uid,
                                                 session)
        if password is None or password != pwd:
            return {'oldMatch': False}
        response['oldMatch'] = True
        response['newMatch'] = user_account.update_password(uid, new_pwd, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Check user password failed: %s', err)
        return response
    finally:
        session.close()
    return response


def count_user():
    """count the number of user in user_account table"""
    session = tables.get_session()
    if session is None:
        return 0
    count = 0
    try:
        user_account = UserAccount()
        uid = user_account.get_max_uid(session)
        if uid is None:
            return 0
        return uid + 1
    except SQLAlchemyError as err:
        LOGGER.error('Count user number failed: %s', err)
        return count
    finally:
        session.close()
    return count


def create_admin(pwd):
    """create admin account"""
    session = tables.get_session()
    if session is None:
        return {'success': False, 'reason': 'failed'}
    try:
        user_account = UserAccount()
        user_account.insert_new_user(0, 'admin@openeuler.org', 'Admin', pwd, session, 'admin')
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Create admin account failed: %s', err)
        return {'success': False, 'reason': 'failed'}
    finally:
        session.close()
    return {'success': True}


def get_user_list():
    """get user details in user_account table"""
    session = tables.get_session()
    if session is None:
        return {'success': False, 'reason': 'failed'}
    try:
        user_account = UserAccount()
        user_account.find_all_user(session)
    except SQLAlchemyError as err:
        LOGGER.error('Get user details failed: %s', err)
        return {'success': False, 'reason': 'failed'}
    finally:
        session.close()
    return {'success': True}


def delete_user(uid):
    """delete user account by uid"""
    session = tables.get_session()
    if session is None:
        return {'success': False, 'reason': 'failed'}
    response = {}
    try:
        user_account = UserAccount()
        user_account.delete_user(uid, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('delete user account failed: %s', err)
        return response
    finally:
        session.close()
    return response


def update_user(uid, pwd, name, role):
    """delete user account by uid"""
    session = tables.get_session()
    if session is None:
        return {'success': False, 'reason': 'failed'}
    response = {}
    try:
        user_account = UserAccount()
        user_account.update_user(uid, pwd, name, role, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('update user account failed: %s', err)
        return response
    finally:
        session.close()
    return response