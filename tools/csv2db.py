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
# Create: 2020-12-21

"""
Tools to convert csv file to data and save to database.
"""

import os
import re
import sys
import argparse
import hashlib
import base64
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, "./../")
from analysis.engine.database import tables, table_collection_data
from analysis.engine.database.trigger_user import user_exist
from analysis.engine.database.trigger_analysis import add_new_collection,\
        change_collection_status, change_collection_info
from analysis.engine.database.table_ip_addrs import IpAddrs


def add_data(path, cip, uid, session):
    """add data to database"""
    if not os.path.exists(path):
        return 'File does not exist', -1
    cid = add_new_collection(cip)
    if cid == -1:
        return 'Failed to add new collection', -1
    try:
        if uid != -1:
            find_or_initial_ip(uid, cip, session)
        table_name = table_collection_data.get_table_name(cip)
        with open(path, 'r', encoding='utf-8') as analysis_file:
            real_headers = analysis_file.readline()[:-1].split(',')
            headers = [re.sub(r'[^\w]', '_', col.lower()) for col in real_headers]
            for index, col in enumerate(headers):
                if not table_collection_data.exist_column(table_name, col, session):
                    table_collection_data.insert_new_column(table_name, col, real_headers[index],
                                                            session)
            keys = '(collection_id, round, ' + ', '.join(col for col in headers)
            vals = '(:collection_id, :round, :' + ', :'.join(col for col in headers)
            keys = keys + ')'
            vals = vals + ')'
            lines = analysis_file.readlines()
            for i, line in enumerate(lines):
                pairs = {'collection_id': cid, 'round': i + 1}
                for k, each in enumerate(line[:-1].split(',')):
                    pairs[headers[k]] = each
                sql = 'insert into ' + table_name + ' ' + keys + ' values ' + vals
                session.execute(text(sql), pairs)
        session.commit()
    except SQLAlchemyError:
        return 'Failed to add collection data to database', -1
    finally:
        session.close()
    return '', cid


def find_or_initial_ip(uid, ip, session):
    """find or initial user ip"""
    ip_table = IpAddrs()
    user_list = ip_table.get_ips_by_uid(uid, session)
    if not ip in user_list:
        ip_table.insert_ip_by_user(ip, uid, session)


if __name__ == '__main__':
    ARG_PARSER = argparse.ArgumentParser(description='Offer path and IP to save data to database')
    ARG_PARSER.add_argument('-p', '--path', required=True,
                            help='Path of csv file that contains data')
    ARG_PARSER.add_argument('-i', '--host', required=True, help='IP that generated file')
    ARG_PARSER.add_argument('-e', '--user_email',
                            help='User email for user that can view this data')
    ARG_PARSER.add_argument('-w', '--password',
                            help='User password for user that can view this data')
    ARGS = ARG_PARSER.parse_args()

    if (not ARGS.user_email and ARGS.password) or (ARGS.user_email and not ARGS.password):
        raise SystemExit('You must offer both email and password for saving data')
    UID = -1
    if ARGS.user_email and ARGS.password:
        hash_code = hashlib.sha256(ARGS.password.encode('utf-8')).digest()
        pwd = base64.b64encode(hash_code).decode('utf-8')
        UID, _ = user_exist(ARGS.user_email, pwd)
        if UID == -1:
            raise SystemExit('Failed to get user by email and password')
    SESSION = tables.get_session()
    if SESSION is None:
        raise SystemExit('Failed to connect to database')
    res, err, CID = add_data(ARGS.path, ARGS.host, UID, SESSION)
    if CID == -1:
        raise SystemExit(err)
    else:
        filename = os.path.split(ARGS.path)[1]
        change_collection_status(CID, ARGS.host, 'finished', 'csv')
        change_collection_info(CID, os.path.splitext(filename)[0])
