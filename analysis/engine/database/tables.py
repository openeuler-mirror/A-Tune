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
Base func for all tables.
"""

import base64
import logging
from configparser import ConfigParser
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

Base = declarative_base()
LOGGER = logging.getLogger(__name__)


def get_session():
    """initial table mapping session"""
    url = get_db_url()
    if url is None:
        return None
    try:
        engine = create_engine(url)
        Base.metadata.create_all(engine, checkfirst=True)
        postgre_session_maker = sessionmaker(bind=engine)
        session = postgre_session_maker()
    except SQLAlchemyError as err:
        LOGGER.error('Connect database failed: %s', err)
        return None
    return session


def decrypted_code(code, key, iv):
    """decrypt code in AES.GCM"""
    if code is None or code == '':
        return ''
    code = convert_to_bytes(code)
    key = convert_to_bytes(key)
    iv = convert_to_bytes(iv)

    decrypts = Cipher(algorithms.AES(key), modes.GCM(iv),
            backend=default_backend()).decryptor()
    res = decrypts.update(code)
    return res.decode('utf-8')


def convert_to_bytes(value):
    """convert value to bytes type"""
    base64_type = value.encode('utf-8')
    return base64.b64decode(base64_type)


def get_db_url():
    """combine engine url according to conf"""
    config = ConfigParser()
    config.read('/etc/atuned/engine.cnf')
    if not config.has_option('database', 'db_enable') or \
            not config.get('database', 'db_enable').lower() == 'true':
        return None
    url = ''
    if config.get('database', 'database').lower() == 'postgresql':
        url += 'postgresql://'
    else:
        return None
    pwd = decrypted_code(config.get('database', 'user_passwd'),
            config.get('database', 'passwd_key'), config.get('database', 'passwd_iv'))
    url += config.get('database', 'user_name') + ':' + pwd + '@' \
            + config.get('database', 'db_host') + ':' + config.get('database', 'db_port') + '/' \
            + config.get('database', 'db_name')

    return url
