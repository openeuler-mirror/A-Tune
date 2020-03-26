#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-10-29

"""
Abstract class of all parsers.
"""

import os
import abc


class Parser:
    """Abstract class of all parsers"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, raw_data_file, data_to_collect, **kwargs):
        """Initialize a parser

        @param raw_data_file: the path of raw data
        @param data_to_collect: list of str which represents the metrics to parse
        @param alias: alias name of output fields
        """
        self._raw_data_file = raw_data_file
        if not os.path.exists(self._raw_data_file):
            raise IOError("No suck file: `{}`".format(self._raw_data_file))
        self._data_to_collect = data_to_collect
        self._iter = None
        self._check_data_to_collect()
        self._prefix = kwargs.get("alias", self.__class__.__name__.lower().replace("parser", ""))

    def __iter__(self):
        """Get the iteration of the parser

        @return: the iteration of the parser
        """
        if not self._iter:
            self._iter = self._get_iter()
        return self._iter

    @abc.abstractmethod
    def _get_supported_metrics(self):
        """Get all supported metrics.

        @return: a list of string which represents the supported metrics
        """

    def _get_extra_supported_metrics(self):
        """Get extra supported metrics and their dependencies.

        @return: a dictionary of which keys are extra supported metrics and
        values are the dependencies of extra supported metrics
        """
        return {}

    def _check_data_to_collect(self):
        """Interface to check data_to_collect. If any metrics in data_to_collect
        is not supported, it will raise ValueError
        """
        supported_data = self._get_supported_metrics()
        extra = self._get_extra_supported_metrics()
        diff = set(self._data_to_collect) - set(supported_data) - set(extra.keys())
        if diff:
            raise ValueError("`{}`: Unknown data name `{}`".format(
                self._raw_data_file, ','.join(diff)))
        for field, dependencies in extra.items():
            if field in self._data_to_collect:
                diff = set(dependencies) - set(supported_data)
                if diff:
                    raise ValueError("`{}`: `{}` need dependencies: `{}`"
                                     .format(self._raw_data_file, field, ','.join(diff)))

    @abc.abstractmethod
    def _get_iter(self):
        """Interface to get the iteration of the parser.

        @return: the iteration of the parser
        """

    def get_data_name(self):
        """Get the names of all data fields.

        @return: a list of string which represents the name of all data fields
        """
        if hasattr(self, "_dev_list"):
            return ["{prefix}.{dev}.{attr}".format(prefix=self._prefix, dev=dev, attr=attr)
                    for dev in getattr(self, "_dev_list")
                    for attr in self._data_to_collect]
        return ["{prefix}.{attr}".format(prefix=self._prefix, attr=attr)
                for attr in self._data_to_collect]

    def get_data_num(self):
        """Get the number of a batch of data

        @return: the number of data
        """
        num = len(self._data_to_collect)
        if hasattr(self, "_dev_list"):
            num *= len(getattr(self, "_dev_list"))
        return num

    def get_next_data(self):
        """Get the next batch of data

        @return: a list of data
        """
        if not self._iter:
            self._iter = self._get_iter()
        data = next(self._iter)
        expect_len = self.get_data_num()
        assert expect_len == len(data), \
            "The data length of {} parser is wrong. Expected {} but get {}.".format(
                self._prefix, expect_len, len(data))
        return data
