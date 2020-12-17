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
Mapping for collection_data table.
"""

import numpy
from analysis.engine.database.tables import Base
from sqlalchemy import Column, VARCHAR, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import func, insert, select

from analysis.engine.database.table_collection import CollectionTable


class CollectionData(Base):
    """mapping collection_data table"""

    __tablename__ = 'collection_data'

    collection_id = Column(Integer, ForeignKey('collection_table.collection_id'))
    round_num = Column(Integer, nullable=False)
    cpu_stat_usr = Column(VARCHAR(255), nullable=True)
    cpu_stat_nice = Column(VARCHAR(255), nullable=True)
    cpu_stat_sys = Column(VARCHAR(255), nullable=True)
    cpu_stat_iowait = Column(VARCHAR(255), nullable=True)
    cpu_stat_irq = Column(VARCHAR(255), nullable=True)
    cpu_stat_soft = Column(VARCHAR(255), nullable=True)
    cpu_stat_steal = Column(VARCHAR(255), nullable=True)
    cpu_stat_guest = Column(VARCHAR(255), nullable=True)
    cpu_stat_util = Column(VARCHAR(255), nullable=True)
    cpu_stat_cutil = Column(VARCHAR(255), nullable=True)
    storage_stat_rs = Column(VARCHAR(255), nullable=True)
    storage_stat_ws = Column(VARCHAR(255), nullable=True)
    storage_stat_rmbs = Column(VARCHAR(255), nullable=True)
    storage_stat_wmbs = Column(VARCHAR(255), nullable=True)
    storage_stat_rrqm = Column(VARCHAR(255), nullable=True)
    storage_stat_wrqm = Column(VARCHAR(255), nullable=True)
    storage_stat_rareq_sz = Column(VARCHAR(255), nullable=True)
    storage_stat_wareq_sz = Column(VARCHAR(255), nullable=True)
    storage_stat_r_await = Column(VARCHAR(255), nullable=True)
    storage_stat_w_await = Column(VARCHAR(255), nullable=True)
    storage_stat_util = Column(VARCHAR(255), nullable=True)
    storage_stat_aqu_sz = Column(VARCHAR(255), nullable=True)
    net_stat_rxkbs = Column(VARCHAR(255), nullable=True)
    net_stat_txkbs = Column(VARCHAR(255), nullable=True)
    net_stat_rxpcks = Column(VARCHAR(255), nullable=True)
    net_stat_txpcks = Column(VARCHAR(255), nullable=True)
    net_stat_ifutil = Column(VARCHAR(255), nullable=True)
    net_estat_errs = Column(VARCHAR(255), nullable=True)
    net_estat_util = Column(VARCHAR(255), nullable=True)
    mem_bandwidth_total_util = Column(VARCHAR(255), nullable=True)
    perf_stat_ipc = Column(VARCHAR(255), nullable=True)
    perf_stat_cache_miss_ratio = Column(VARCHAR(255), nullable=True)
    perf_stat_mpki = Column(VARCHAR(255), nullable=True)
    perf_stat_itlb_load_miss_ratio = Column(VARCHAR(255), nullable=True)
    perf_stat_dtlb_load_miss_ratio = Column(VARCHAR(255), nullable=True)
    perf_stat_sbpi = Column(VARCHAR(255), nullable=True)
    perf_stat_sbpc = Column(VARCHAR(255), nullable=True)
    mem_vmstat_procs_b = Column(VARCHAR(255), nullable=True)
    mem_vmstat_io_bo = Column(VARCHAR(255), nullable=True)
    mem_vmstat_system_in = Column(VARCHAR(255), nullable=True)
    mem_vmstat_system_cs = Column(VARCHAR(255), nullable=True)
    mem_vmstat_util_swap = Column(VARCHAR(255), nullable=True)
    mem_vmstat_util_cpu = Column(VARCHAR(255), nullable=True)
    mem_vmstat_procs_r = Column(VARCHAR(255), nullable=True)
    sys_tasks_procs = Column(VARCHAR(255), nullable=True)
    sys_tasks_cswchs = Column(VARCHAR(255), nullable=True)
    sys_ldavg_runq_sz = Column(VARCHAR(255), nullable=True)
    sys_ldavg_plist_sz = Column(VARCHAR(255), nullable=True)
    sys_ldavg_ldavg_1 = Column(VARCHAR(255), nullable=True)
    sys_ldavg_ldavg_5 = Column(VARCHAR(255), nullable=True)
    sys_fdutil_fd_util = Column(VARCHAR(255), nullable=True)
    fk_collection = relationship(CollectionTable, backref='collection_data')

    __table_args__ = (
        PrimaryKeyConstraint('collection_id', 'round_num', name='pk_collection_data'),
    )

    def __repr__(self):
        return "<collection_data(collection_id='%s', round_num='%s')>"\
                % (self.collection_id, self.round_num)

    @staticmethod
    def insert_collection_data(cid, rounds, data, session):
        """insert new collection data to table"""
        val = [cid, rounds]
        for element in data.split(' '):
            val.append(element)
        sql = insert(CollectionData).values(tuple(val))
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def get_max_round(cid, session):
        """get max round_num by collection_id"""
        rounds = session.query(func.max(CollectionData.round_num))\
                .filter(CollectionData.collection_id == cid).scalar()
        if rounds is None or rounds == -1:
            rounds = 0
        return rounds

    @staticmethod
    def get_line(cid, line_start, line_end, session):
        """get selected line by cid and line range"""
        sql = select([CollectionData]).where(CollectionData.collection_id == cid)\
                .where(CollectionData.round_num > line_start)\
                .where(CollectionData.round_num <= line_end)
        res = session.execute(sql).fetchall()
        if len(res) == 0:
            return [], []
        if cid == -1:
            return list(res[0])[2:], []
        rounds = [row[1] for row in res]
        res = [list(row)[2:] for row in res]
        res = numpy.array(res).T.tolist()
        return res, rounds
