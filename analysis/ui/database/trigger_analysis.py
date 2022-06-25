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
Triggers to action analysis database.
"""

import logging
from sqlalchemy.exc import SQLAlchemyError

from analysis.ui.database import tables, table_collection_data
from analysis.ui.database.table_ip_addrs import IpAddrs
from analysis.ui.database.table_collection import CollectionTable
from analysis.ui.database.table_analysis_log import AnalysisLog

LOGGER = logging.getLogger(__name__)


def add_new_collection(cip):
    """add new collection to collection_table"""
    session = tables.get_session()
    cid = -1
    if session is None:
        return cid
    try:
        ip_table = IpAddrs()
        if not ip_table.find_ip(cip, session):
            ip_table.insert_ip_by_user(cip, 0, session)
            table_name = table_collection_data.get_table_name(cip)
            table_collection_data.initial_table(table_name, session)
        collection_table = CollectionTable()
        cid = collection_table.get_max_cid(session) + 1
        collection_table.insert_new_collection(cid, cip, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Add new collection to collection_table failed: %s', err)
        return -1
    finally:
        session.close()
    return cid


def add_collection_data(cid, cip, data):
    """add collection data to collection_ip table"""
    session = tables.get_session()
    if session is None:
        return
    try:
        rounds = table_collection_data.get_max_round(cid, cip, session) + 1
        res = table_collection_data.insert_table(cid, rounds, cip, data, session)
        if not res:
            LOGGER.error('Failed to insert data to collection_table')
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Add collection data to collection_table failed: %s', err)
    finally:
        session.close()


def add_analysis_log(cid, data):
    """add log to analysis_log table"""
    session = tables.get_session()
    if session is None:
        return
    try:
        analysis_log = AnalysisLog()
        rounds = analysis_log.get_max_round(cid, session) + 1
        analysis_log.insert_log(cid, rounds, data, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Add new log data to analysis_log failed: %s', err)
    session.close()


def change_collection_status(cid, cip, status, types):
    """change status of collection_table"""
    session = tables.get_session()
    if session is None:
        return
    try:
        collection_table = CollectionTable()
        curr_status = collection_table.get_field_by_key(CollectionTable.collection_status,
                                                        CollectionTable.collection_id,
                                                        cid, session)
        if curr_status != status:
            collection_table.update_status(cid, status, session)

        if types == 'csv':
            rounds = table_collection_data.get_max_round(cid, cip, session)
            collection_table.update_total_round(cid, rounds, session)
        else:
            analysis_log = AnalysisLog()
            logs = analysis_log.get_max_round(cid, session)
            collection_table.update_total_log(cid, logs, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Change collection status failed: %s', err)
    session.close()


def change_collection_info(cid, workload):
    """change name & workload of collection_table"""
    session = tables.get_session()
    if session is None:
        return
    try:
        collection_table = CollectionTable()
        curr_workload = collection_table.get_field_by_key(CollectionTable.workload_type,
                                                          CollectionTable.collection_id,
                                                          cid, session)
        if curr_workload is None or curr_workload == '':
            names = collection_table.get_field_by_key(CollectionTable.collection_name,
                    CollectionTable.collection_id, cid, session)
            names = workload + '-' + names
            collection_table.update_name(cid, names, session)
            if workload != 'csv_convert':
                collection_table.update_workload(cid, workload, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Change name and workload of collection_table failed: %s', err)
    session.close()


def get_analysis_list(uid):
    """get all analysis with user_id 'uid' as a list"""
    session = tables.get_session()
    if session is None:
        return None
    try:
        ip_table = IpAddrs()
        collection_table = CollectionTable()
        ips = ip_table.get_ips_by_uid(uid, session)
        res = []
        for cip in ips:
            res.extend(collection_table.get_all_collection_by_ip(cip, session))
        if len(res) > 0:
            res = sorted(res, key=(lambda x:x['date']), reverse=True)
    except SQLAlchemyError as err:
        LOGGER.error('Get analysis list failed: %s', err)
        return None
    finally:
        session.close()
    return res


def rename_collection(name, new_name):
    """rename collecton from 'name' to 'new_name' """
    session = tables.get_session()
    if session is None:
        return False, 'connect'
    try:
        collection_table = CollectionTable()
        if not collection_table.check_exist_by_name(CollectionTable, name, session):
            return False, 'collection not exist'
        if collection_table.check_exist_by_name(CollectionTable, new_name, session):
            return False, 'duplicate'
        collection_table.update_collection_name(name, new_name, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Rename collection failed: %s', err)
        return False, 'error'
    finally:
        session.close()
    return True, ''


def collection_exist(name):
    """check if collection exist"""
    exist = False
    session = tables.get_session()
    if session is None:
        return exist
    try:
        collection_table = CollectionTable()
        exist = collection_table.check_exist_by_name(CollectionTable, name, session)
    except SQLAlchemyError as err:
        LOGGER.error('Check if collection exist failed: %s', err)
    session.close()
    return exist


def get_collection_data_dirs(cip, cid, csv_line, response, session):
    """get collection data"""
    header, _ = table_collection_data.get_line(cip, -1, -2, -1, session)
    data, response['round'] = table_collection_data.get_line(cip, cid, csv_line, csv_line + 10,
                                                             session)
    for i, val in enumerate(data):
        if val[0] is None:
            del data[i]
            del header[i]
    response['table_header'] = header
    response['csv_data'] = data
    if len(response['csv_data']) == 0:
        response['nextCsv'] = csv_line + 0
    else:
        response['nextCsv'] = len(response['csv_data'][0])


def get_analysis_log_dirs(cid, log_line, response, session):
    """get analysis log data"""
    analysis_log = AnalysisLog()
    response['log_data'] = analysis_log.get_line(cid, log_line, log_line + 10, session)
    response['nextLog'] = log_line + len(response['log_data'])


def get_analysis_data(name, csv_line, log_line):
    """get each round data"""
    session = tables.get_session()
    if session is None:
        return {'isExist': False}
    response = {}
    try:
        collection_table = CollectionTable()
        cid = collection_table.get_field_by_key(CollectionTable.collection_id,
                                                CollectionTable.collection_name, name, session)
        cip = collection_table.get_field_by_key(CollectionTable.collection_ip,
                                                CollectionTable.collection_name, name, session)
        get_collection_data_dirs(cip, cid, csv_line, response, session)
        get_analysis_log_dirs(cid, log_line, response, session)
        workload = collection_table.get_field_by_key(CollectionTable.workload_type,
                CollectionTable.collection_id, cid, session)
        if workload is not None:
            response['workload'] = workload
        status = collection_table.get_field_by_key(CollectionTable.collection_status,
                                                   CollectionTable.collection_id, cid, session)
        if csv_line < response['nextCsv'] or log_line < response['nextLog']:
            response['hasNext'] = True
            response['interval'] = 0
        elif status == 'running':
            response['hasNext'] = True
            response['interval'] = 5000
        else:
            response['hasNext'] = False
    except SQLAlchemyError as err:
        LOGGER.error('Get analysis data failed: %s', err)
        return {'isExist': False}
    finally:
        session.close()
    response['isExist'] = True
    return response


def get_compare_collection(name, csv_line):
    """get compare collection data"""
    session = tables.get_session()
    if session is None:
        return {'isExist': False}
    response = {}
    try:
        collection_table = CollectionTable()
        cid = collection_table.get_field_by_key(CollectionTable.collection_id,
                                                CollectionTable.collection_name, name, session)
        cip = collection_table.get_field_by_key(CollectionTable.collection_ip,
                                                CollectionTable.collection_name, name, session)
        get_collection_data_dirs(cip, cid, csv_line, response, session)
        if csv_line < response['nextCsv']:
            response['hasNext'] = True
        else:
            response['hasNext'] = False
    except SQLAlchemyError as err:
        LOGGER.error('Get compare collection data failed: %s', err)
        return {'isExist': False}
    finally:
        session.close()
        response['isExist'] = True
    return response
