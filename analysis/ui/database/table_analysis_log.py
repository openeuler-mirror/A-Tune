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
Mapping for analysis_log table.
"""

from sqlalchemy import Column, VARCHAR, Integer, PrimaryKeyConstraint
from sqlalchemy import func, insert, select

from analysis.ui.database.tables import BASE


class AnalysisLog(BASE):
    """mapping analysis_log table"""

    __tablename__ = 'analysis_log'

    analysis_id = Column(Integer, nullable=False)
    round_num = Column(Integer, nullable=False)
    section = Column(VARCHAR(255), nullable=False)
    status = Column(VARCHAR(255), nullable=False)
    analysis_key = Column(VARCHAR(255), nullable=False)
    analysis_value = Column(VARCHAR(255), nullable=False)
    notes = Column(VARCHAR(255), nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('analysis_id', 'round_num', name='pk_analysis_log'),
    )

    def __repr__(self):
        return "<analysis_log(analysis='%s %s %s %s %s %s', id='%s')>" % \
                (self.round_num, self.section, self.status, self.analysis_key, self.analysis_value,
                 self.notes, self.fk_analysis)

    @staticmethod
    def insert_log(aid, rounds, data, session):
        """insert new log into analysis_log table"""
        val = [aid, rounds]
        for element in data.split('|'):
            val.append(element)
        sql = insert(AnalysisLog).values(tuple(val))
        res = session.execute(sql)
        return res is not None

    @staticmethod
    def get_max_round(aid, session):
        """get max round_num by analysis_id"""
        rounds = session.query(func.max(AnalysisLog.round_num)) \
                .filter(AnalysisLog.analysis_id == aid).scalar()
        return 0 if rounds is None else rounds


    @staticmethod
    def get_line(aid, line_start, line_end, session):
        """get selected line by cid and line range"""
        sql = select([AnalysisLog]).where(AnalysisLog.analysis_id == aid) \
                .where(AnalysisLog.round_num > line_start) \
                .where(AnalysisLog.round_num <= line_end)
        res = session.execute(sql).fetchall()
        if len(res) == 0:
            return []
        res = [list(row)[2:] for row in res]
        return res