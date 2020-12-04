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
Triggers to action analysis database.
"""

import logging
from sqlalchemy.exc import SQLAlchemyError

from analysis.engine.database import tables
from analysis.engine.database.table_ip_addrs import IpAddrs
from analysis.engine.database.table_collection import CollectionTable
from analysis.engine.database.table_analysis_log import AnalysisLog
from analysis.engine.database.table_collection_data import CollectionData

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


def add_collection_data(cid, data):
    """add collection data to collection_data table"""
    session = tables.get_session()
    if session is None:
        return
    try:
        collection_data = CollectionData()
        rounds = collection_data.get_max_round(cid, session) + 1
        collection_data.insert_collection_data(cid, rounds, data, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Add new collection data to collection_data failed: %s', err)
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


def change_collection_status(cid, status, types):
    """change status of collection_table"""
    session = tables.get_session()
    if session is None:
        return
    try:
        collection_table = CollectionTable()
        curr_status = collection_table.get_field_by_cid(CollectionTable.collection_status, cid, session)
        if curr_status != status:
            collection_table.update_status(cid, status, session)

        if types == 'csv':
            collection_data = CollectionData()
            rounds = collection_data.get_max_round(cid, session)
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
        curr_workload = collection_table.get_field_by_cid(CollectionTable.workload_type, cid, session)
        if curr_workload is None or curr_workload == '':
            names = collection_table.get_field_by_cid(CollectionTable.collection_name, cid, session)
            names = workload + '-' + names
            collection_table.update_name(cid, names, session)
            collection_table.update_workload(cid, workload, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Change name and workload of collection_table failed: %s', err)
    session.close()
