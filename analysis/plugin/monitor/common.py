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
The base class of the monitor, used to report the given config, get the collected info,
decode the collected info, format the collected info and output collected info to file.
"""
import inspect
import logging

LOGGER = logging.getLogger(__name__)


class Monitor():
    """Base class for monitors"""

    # sub class should init these
    _module = "UNKNOWN"
    _purpose = "UNKNOWN"

    # for inner options usage
    _option = ""

    def __init__(self, user=None):
        """
        Initialize.

        :param user(optional): "UT" for unit test, others are ignored
        :returns: None
        :raises: None
        """
        self._user = user

    def module(self):
        """
        Get the the module of this monitor.

        :param: None
        :returns: The module of this monitor
        :raises: None
        """
        return self._module

    def purpose(self):
        """
        Get the the purpose of this monitor.

        :param: None
        :returns: The purpose of this monitor
        :raises: None
        """
        return self._purpose

    def _getopt(self):
        """
        Get the the inner option of this monitor.
        Multi-options should be splited by ";".

        :param: None
        :returns: The iterator for get all inner options
        :raises: None
        """
        return iter(self._option.split(";"))

    @staticmethod
    def _getpara(paras):
        """
        Get all the configs from one string.

        :param paras: The configs string splited by ";"
        :returns None: No parameter
        :returns parameter: next parameter
        :raises: None
        """
        if paras is None:
            return None

        try:
            nextp = next(paras)
        except StopIteration:
            return None

        if nextp == "":
            nextp = None
        return nextp

    def report(self, fmt, path, para=None):
        """
        Report the given config.

        :param fmt: The option for format(fmt)
        :param path: The path to output, None for pass through
        :param para: Multi-options for get(para) and decode(para), should be splited by ";"
        :returns None: Success
        :returns info: Success, output info
        :returns Exceptions: Fail, with info
        :raises: None
        """
        try:
            if para is None:
                paras = None
            else:
                paras = iter(para.split(";"))
            info = self._get(self._getpara(paras))
            decoded_info = self.decode(info, self._getpara(paras))
            fmted_info = self.format(decoded_info, fmt)
            return self.output(fmted_info, path)
        except Exception as err:
            if self._user == "UT":
                raise err
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            return err

    def _get(self, para):
        """
        The inner method to get collected info.
        The sub class should implement this method.

        :param para: The option for get,
                [%s]:
                "--interval=" to specify period of time
                "--cpu=" to select which cpu
                "--event=" to select which event
        :returns value: Success, collected info string
        :raises Exceptions: Fail, with info
        """
        err = NotImplementedError("_get method is not implemented")
        LOGGER.error("%s.%s: %s", self.__class__.__name__,
                     inspect.stack()[0][3], str(err))
        raise err

    def get(self, para=None):
        """
        Get the collected info.

        :param para(optional): The option for get
        :returns info: Success, collected info string
        :returns Exceptions: Fail, error in _get()
        :raises: None
        """
        try:
            ret = self._get(para)
        except Exception as err:
            if self._user == "UT":
                raise err
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            return err
        return ret

    def decode(self, info, para):
        """
        The inner method to decode collected info.

        :param info: The collected info string
        :param para: The option for decode,
                [%s]:
                "--fields=" to select which data
                "--cpu=" to select which cpu
                "--nic=" to select which net interface
                "--device=" to select which device
        :returns info: Success, decoded info
        :raises NotImplementedError: Error, not supported
        :raises Exceptions: Fail, with info
        """
        if para is None:
            return info
        err = NotImplementedError("Not supported decode: {}".format(para))
        LOGGER.error("%s.%s: %s", self.__class__.__name__,
                     inspect.stack()[0][3], str(err))
        raise err

    def format(self, info, fmt):
        """
        The inner method to format collected info.

        :param info: The decoded info
        :param fmt: The option for format,
                [raw, data, %s]:
                "raw" for original string
                "xml" for xml string
                "json" for json string
                "data" for list of decoded data string
                "table" for pretty table string
        :returns info: Success, formatted info
        :raises NotImplementedError: Error, not supported
        :raises Exceptions: Fail, with info
        """
        if fmt == "raw":
            return info
        if fmt == "data":
            return info.split()
        err = NotImplementedError("Not supported format: {}".format(fmt))
        LOGGER.error("%s.%s: %s", self.__class__.__name__,
                     inspect.stack()[0][3], str(err))
        raise err

    @staticmethod
    def output(info, path):
        """
        The method to output collected info to file.

        :param info: The formatted info
        :param path: The path to output, None for pass through
        :returns None: Success
        :returns info: Success, output info
        :raises: None
        """
        if path is None:
            return info

        with open(path, mode='w', buffering=-1, encoding=None, errors=None, newline=None) as file:
            file.write(info)
        return None


def walk_class_type(father, class_type, desc, datas):
    """get key field"""
    if "class" in father and father["class"] == class_type:
        if "description" in father and (desc is None or father["description"] == desc):
            datas.append(father)
            return
    if "children" in father:
        for i in father["children"]:
            walk_class_type(i, class_type, desc, datas)


def get_class_type(json_content, class_type, desc=None):
    """convert json formatted content to dict"""
    datas = []
    walk_class_type(json_content, class_type, desc, datas)
    dict_datas = {}
    dict_datas[class_type + "s"] = datas
    return dict_datas
