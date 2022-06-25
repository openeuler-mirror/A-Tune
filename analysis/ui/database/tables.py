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
Mapping for ip_addrs table.
"""

from sqlalchemy import Column, VARCHAR, Integer, PrimaryKeyConstraint
from sqlalchemy import insert, select

from analysis.ui.database.tables import BASE


class IpAddrs(BASE):
    """mapping ip_addrs table"""

    __tablename__ = 'ip_addrs'

    user_id = Column(Integer, nullable=False)
    ip = Column(VARCHAR(255), nullable=False)
    ip_status = Column(VARCHAR(255), nullable=False, default='rest')

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'ip', name='pk_ip_addrs'),
    )

    def __repr__(self):
        return "<ip_addrs(ip='%s %s', fk_user='%s')>" % (self.ip, self.ip_status, self.fk_user)

    @staticmethod
    def find_ip(check_ip, session):
        """find check_ip in ip_addrs table"""
        sql = select([IpAddrs]).where(IpAddrs.ip == check_ip)
        res = session.execute(sql).scalar()
        return res is not None

    @staticmethod
    def insert_ip_by_user(iip, uid, session):
        """insert iip and uid into ip_addrs table"""
        sql = insert(IpAddrs).values(user_id=uid, ip=iip)
        inserts = session.execute(sql)
        return inserts is not None

    @staticmethod
    def get_ips_by_uid(uid, session):
        """get all ips by user_id"""
        sql = select([IpAddrs.ip]).where(IpAddrs.user_id == uid)
        tuples = session.execute(sql).fetchall()
        res = []
        for each_line in tuples:
            res.append(each_line[0])
        return res

    @staticmethod
    def check_exist_by_ip(ip_addr, uid, session):
        """check if (uid, ip) exist"""
        sql = select([IpAddrs]).where(IpAddrs.user_id == uid).where(IpAddrs.ip == ip_addr)
        return session.execute(sql).scalar() is not None
[root@localhost database]# cat tables.py
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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from analysis.ui.config import UiConfig

BASE = declarative_base()
LOGGER = logging.getLogger(__name__)


def get_session():
    """initial table mapping session"""
    url = get_db_url()
    if url is None:
        return None
    try:
        engine = create_engine(url)
        BASE.metadata.create_all(engine, checkfirst=True)
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
    if not UiConfig.db_enable:
        return None
    url = ''
    if UiConfig.database.lower() == 'postgresql':
        url += 'postgresql://'
    elif UiConfig.database.lower() == 'mysql':
        url += 'mysql+pymysql://'
    else:
        return None
    pwd = decrypted_code(UiConfig.user_passwd, UiConfig.passwd_key, UiConfig.passwd_iv)
    url += UiConfig.user_name + ':' + pwd + '@' + UiConfig.db_host + ':' \
           + UiConfig.db_port + '/' + UiConfig.db_name
    return url
