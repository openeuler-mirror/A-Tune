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
Triggers to action tuning database.
"""

import logging
import time
import string
from sqlalchemy import text, MetaData, create_engine
from sqlalchemy.exc import SQLAlchemyError

from analysis.ui.database import tables, table_tuning_data
from analysis.ui.database.table_ip_addrs import IpAddrs
from analysis.ui.database.table_tuning import TuningTable
from analysis.ui.database.table_command import CommandTable

LOGGER = logging.getLogger(__name__)


def add_new_tuning(name, engine, rounds, tip):
    """add new tuning to tuning_table"""
    session = tables.get_engine_session()
    if session is None:
        return
    try:
        ip_table = IpAddrs()
        if not ip_table.find_ip(tip, session):
            ip_table.insert_ip_by_user(ip=tip, uid=0, session=session)
        localtime = time.localtime()
        tuning_table = TuningTable()
        tid = tuning_table.get_max_tid(session) + 1
        tuning_table.insert_new_tuning(tid, name, engine, rounds, tip, localtime, session)
        command_table = CommandTable()
        cid = command_table.get_max_cid(session) + 1
        command_table.insert_new_command(cid, tid, 'tuning', name, tip, localtime, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Add new tuning to tuning_table failed: %s', err)
    session.close()


def change_tuning_baseline(name, val):
    """change baseline info"""
    session = tables.get_engine_session()
    if session is None:
        return
    try:
        tuning_table = TuningTable()
        tuning_table.update_baseline(name, val, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Change tuning baseline value failed: %s', err)
    session.close()


def create_tuning_data_table(name, line):
    """create new tuning_data table"""
    session = tables.get_engine_session()
    if session is None:
        return
    try:
        table_name = 'tuning_' + name
        if not table_tuning_data.exists_table(table_name):
            metadata = MetaData()
            table, init_key, init_val, pairs = table_tuning_data.initial_table(table_name, metadata,
                                                                            line)
            if table is None:
                LOGGER.info('Data in tuning_data does not match what desired')
                return
            engine = create_engine(tables.get_engine_db_url())
            metadata.create_all(engine)
            sql = 'insert into ' + table_name + ' ' + init_key + ' values ' + init_val
            session.execute(text(sql), pairs)
            session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Create new tuning data table failed: %s', err)
    finally:
        session.close()


def add_tuning_data(name, iters, line):
    """add new round to tuning_data table"""
    session = tables.get_engine_session()
    if session is None:
        return None
    try:
        tuning_table = TuningTable()
        tid = str(tuning_table.get_field_by_name(TuningTable.tuning_id, name, session))
        table_name = 'tuning_' + name.rstrip(string.digits)[:-1]
        if not table_tuning_data.exists_table(table_name):
            create_tuning_data_table(table_name, line)
        keys, vals, pairs = table_tuning_data.execute_tuning_data(table_name, tid, iters, line, session)
        if keys is None:
            LOGGER.info('Data in tuning_data does not match what desired')
            return None
        sql = 'insert into ' + table_name + ' ' + keys + ' values ' + vals
        session.execute(text(sql), pairs)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Add new round to tuning_data table failed: %s', err)
        return None
    finally:
        session.close()
    return table_name


def change_tuning_status(table_name, name):
    """change tuning_table status"""
    session = tables.get_engine_session()
    if session is None:
        return None
    try:
        tuning_table = TuningTable()
        total_round = tuning_table.get_field_by_name(TuningTable.total_round, name, session)
        data_round = session.execute('select max(' + table_name + '._round) from ' + \
                table_name).scalar()
        if total_round is not None and total_round == data_round:
            tuning_table.update_status(name, 'finished', session)
            command_table = CommandTable()
            command_table.update_status_by_name(name, 'finished', session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Change tuning_table status failed: %s', err)
    session.close()


def count_tuning_list(uid):
    """count the number of tuning list in tuning_table table"""
    session = tables.get_session()
    if session is None:
        return None
    try:
        ip_table = IpAddrs()
        tuning_table = TuningTable()
        ips = ip_table.get_ips_by_uid(uid, session)
        count = 0
        for tip in ips:
            count += tuning_table.count_all_collection_by_ip(tip['ipAddrs'], session)
    except SQLAlchemyError as err:
        LOGGER.error('Count tuning list failed: %s', err)
        return None
    finally:
        session.close()
    return count


def get_tuning_list(uid, page_num, page_size):
    """get the page_size data in page_num page with user_id 'uid' as a list"""
    session = tables.get_session()
    if session is None:
        return None
    try:
        ip_table = IpAddrs()
        tuning_table = TuningTable()
        ips = ip_table.get_ips_by_uid(uid, session)
        res = []
        ips = [ip['ipAddrs'] for ip in ips]
        res.extend(tuning_table.get_command_by_ip(ips, page_num, page_size, session))
        if len(res) > 0:
            res = sorted(res, key=(lambda x:x['date']), reverse=True)
    except SQLAlchemyError as err:
        LOGGER.error('Get analysis list failed: %s', err)
        return None
    finally:
        session.close()
    return res


def get_all_tuning_list(uid, status):
    """get all tuning with status 'status' as a list"""
    session = tables.get_session()
    if session is None:
        return None
    try:
        ip_table = IpAddrs()
        tuning_table = TuningTable()
        ips = ip_table.get_ips_by_uid(uid, session)
        res = []
        for tip in ips:
            if status == 'all':
                res.extend(tuning_table.get_all_tunings_by_ip(tip['ipAddrs'], session))
            else:
                res.extend(tuning_table.get_status_tuning_by_ip(status['ipAddrs'], tip, session))
        if len(res) > 0:
            res = sorted(res, key=(lambda x:x['date']), reverse=True)
    except SQLAlchemyError as err:
        LOGGER.error('Get tuning list failed: %s', err)
        return None
    finally:
        session.close()
    return res


def rename_tuning(name, new_name):
    """rename tuning"""
    session = tables.get_session()
    if session is None:
        return False, 'connect'
    try:
        tuning_table = TuningTable()
        if not tuning_table.check_exist_by_name(TuningTable, name, session):
            return False, 'tuning not exist'
        if tuning_table.check_exist_by_name(TuningTable, new_name, session):
            return False, 'duplicate'
        tuning_table.update_tuning_name(name, new_name, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Rename tuning failed: %s', err)
        return False, 'error'
    finally:
        session.close()
    return True, ''


def tuning_exist(name):
    """check if tuning exist"""
    exist = False
    session = tables.get_session()
    if session is None:
        return exist
    try:
        tuning_table = TuningTable()
        exist = tuning_table.check_exist_by_name(TuningTable, name, session)
    except SQLAlchemyError as err:
        LOGGER.error('Check if tuning exist failed: %s', err)
    session.close()
    return exist


def get_tuning_info(status, name):
    """get info about tuning"""
    session = tables.get_session()
    if session is None:
        return {'isExist': False}
    response = {}
    try:
        tuning_table = TuningTable()
        response['status'] = status
        response['file_name'] = name
        response['engine'] = tuning_table.get_field_by_name(TuningTable.tuning_engine, name,
                                                            session)
        response['round'] = tuning_table.get_field_by_name(TuningTable.total_round, name, session)
        response['base'] = tuning_table.get_field_by_name(TuningTable.baseline, name, session)
        tid = tuning_table.get_field_by_name(TuningTable.tuning_id, name, session)
        response['parameter'] = table_tuning_data.get_param_by_table_name('tuning_' + str(tid),
                                                                          session)
        response['line'] = 0
    except SQLAlchemyError as err:
        LOGGER.error('Get tuning info failed: %s', err)
        return {'isExist': False}
    finally:
        session.close()
    response['isExist'] = True
    return response


def get_tuning_data(status, name, line):
    """get each round data"""
    session = tables.get_session()
    if session is None:
        return {'isExist': False}
    response = {}
    try:
        tuning_table = TuningTable()
        response['status'] = status
        response['file_name'] = name
        response['initial_line'] = int(line)
        tid = tuning_table.get_field_by_name(TuningTable.tuning_id, name, session)
        total_round = tuning_table.get_field_by_name(TuningTable.total_round, name, session)
        table_name = 'tuning_' + str(tid)
        response['parameter'] = table_tuning_data.get_param_by_table_name(table_name, session)
        response['line'], response['cost'], response['data'] = \
                table_tuning_data.get_tuning_data(total_round, table_name, line, session)
    except SQLAlchemyError as err:
        LOGGER.error('Get tuning data failed: %s', err)
        return {'isExist': False}
    finally:
        session.close()
    response['isExist'] = True
    return response


def get_tuning_status(name):
    """get tuning status"""
    session = tables.get_session()
    if session is None:
        return 'break'
    status = 'break'
    try:
        tuning_table = TuningTable()
        status = tuning_table.get_field_by_name(TuningTable.tuning_status, name, session)
    except SQLAlchemyError as err:
        LOGGER.error('Get tuning status failed: %s', err)
    session.close()
    return status


def update_tuning_description(tid, description):
    """update one tuning record description by cid"""
    session = tables.get_session()
    if session is None:
        return None
    res = False
    try:
        tuning_table = TuningTable()
        res = tuning_table.update_description(tid, description, session)
        command_table = CommandTable()
        command_id = command_table.get_cid_by_mid_and_type(tid, 'tuning', session)
        res = command_table.update_description(command_id, description, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Update analysis description failed: %s', err)
        return None
    finally:
        session.close()
    return res