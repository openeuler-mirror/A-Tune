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
# Create: 2023-2-16

"""
Triggers to action command database.
"""

import logging
from sqlalchemy.exc import SQLAlchemyError

from analysis.ui.database import tables
from analysis.ui.database.table_ip_addrs import IpAddrs
from analysis.ui.database.table_command import CommandTable
from analysis.ui.database.table_collection import CollectionTable
from analysis.ui.database.table_tuning import TuningTable

LOGGER = logging.getLogger(__name__)


def count_command_list(uid):
    """count the number of command list in command_table table"""
    session = tables.get_session()
    if session is None:
        return None
    try:
        ip_table = IpAddrs()
        command_table = CommandTable()
        ips = ip_table.get_ips_by_uid(uid, session)
        count = 0
        for cip in ips:
            count += command_table.count_all_command_by_ip(cip['ipAddrs'], session)
    except SQLAlchemyError as err:
        LOGGER.error('Count analysis list failed: %s', err)
        return None
    finally:
        session.close()
    return count


def get_command_list(uid, page_num, page_size):
    """get the page_size data in page_num page with user_id 'uid' as a list"""
    session = tables.get_session()
    if session is None:
        return None
    try:
        ip_table = IpAddrs()
        command_table = CommandTable()
        ips = ip_table.get_ips_by_uid(uid, session)
        res = []
        ips = [ip['ipAddrs'] for ip in ips]
        res.extend(command_table.get_command_by_ip(ips, page_num, page_size, session))
        if len(res) > 0:
            res = sorted(res, key=(lambda x:x['date']), reverse=True)
    except SQLAlchemyError as err:
        LOGGER.error('Get analysis list failed: %s', err)
        return None
    finally:
        session.close()
    return res


def update_command_description(cid, description):
    """update one command record description by cid"""
    session = tables.get_session()
    if session is None:
        return None
    res = False
    try:
        command_table = CommandTable()
        res = command_table.update_description(cid, description, session)
        mid = command_table.get_field_by_key(CommandTable.command_map_id, 
                                             CommandTable.command_id, cid, session)
        mtype = command_table.get_field_by_key(CommandTable.command_type, 
                                             CommandTable.command_id, cid, session)
        if type == 'analysis':
            collection_table = CollectionTable()
            res = collection_table.update_description(mid, description, session)
        else:
            tuning_table = TuningTable()
            res = tuning_table.update_description(mid, description, session)
        session.commit()
    except SQLAlchemyError as err:
        LOGGER.error('Update command description failed: %s', err)
        return None
    finally:
        session.close()
    return res