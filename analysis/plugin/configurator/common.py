#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-10-29

"""
The base class of the configuration, used to set the value, get the value of the given key,
backup from the given config and resume from the saved config info.
"""
import inspect
import logging
import json
from functools import wraps

from ..public import SetConfigError

LOGGER = logging.getLogger(__name__)


class Configurator:
    """Base class for configurators"""

    # sub class should init these
    _module = "UNKNOWN"
    _submod = "UNKNOWN"

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
        Get the the module of this configurator.

        :param: None
        :returns: The module of this configurator
        :raises: None
        """
        return self._module

    def submod(self):
        """
        Get the the sub module of this configurator.

        :param: None
        :returns: The sub module of this configurator
        :raises: None
        """
        return self._submod

    def _getopt(self):
        """
        Get the the inner option of this configurator.
        Multi-options should be splited by ";".

        :param: None
        :returns: The iterator for get all inner options
        :raises: None
        """
        return iter(self._option.split(";"))

    def set(self, config):
        """
        Set the given config.

        :param config: The config to be setted, string like "key = value"
        :returns None: Success
        :returns NeedRebootWarning: Success, but need reboot
        :returns SetConfigError: Fail, fail in _set()
        :returns Exceptions: Fail, error in _set()
        :raises Exceptions: Error, unexpected errors
        """
        cfg = self._getcfg(config)
        try:
            ret = self._set(cfg[0], cfg[1])
        except Exception as err:
            if self._user == "UT":
                raise err
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            return err

        if (ret == 0) and self.check(cfg[1], self.get(cfg[0], cfg[1])):
            err = None
        elif cfg[1] is None:
            err = SetConfigError(
                "Fail to set {mod}.{sub} config: {key}".format(
                    mod=self.module(), sub=self.submod(), key=cfg[0]))
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
        else:
            err = SetConfigError("Fail to set {mod}.{sub} config: {key}={val}".format(
                mod=self.module(), sub=self.submod(), key=cfg[0], val=cfg[1]))
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
        return err

    @staticmethod
    def _precheck(key, value, file):
        """
        The common method to precheck config.

        :param key: The config key
        :param value: The config value
        :param file: The check file
        :returns None: Success
        :raises TypeError: Fail, invalid rule
        :raises ValueError: Fail, invalid value
        :raises KeyError: Fail, invalid key
        :raises Exceptions: Fail, with info
        """
        with open(file, 'r') as data:
            ctx = data.read()
            check_rules = json.loads(ctx)

        if type(check_rules).__name__ != 'dict':
            raise TypeError("Invalid rule file")

        rule = check_rules.get(key)
        if type(rule).__name__ == 'NoneType':
            raise KeyError('Invalid key "{}"'.format(key))
        if type(rule).__name__ == 'list':
            if value in rule:
                return None
        elif type(rule).__name__ == 'dict':
            start = rule.get("start")
            end = rule.get("end")
            step = rule.get("step")
            try:
                ranges = list(range(start, end, step))
            except BaseException:
                raise TypeError("Invalid rule")
            if int(value) in ranges:
                return None
        else:
            raise TypeError(
                "Invalid rule type: {}".format(
                    type(rule).__name__))
        raise ValueError('Invalid value "{}" for key "{}"'.format(value, key))

    def _set(self, key, value):
        """
        The inner method to set config.
        The sub class should implement this method.

        :param key: The config key,
                [%s]
        :param value: The config value,
                [%s]
        :returns 0: Success
        :returns errno: Fail
        :raises Exceptions: Fail, with info
        """
        err = NotImplementedError("_set method is not implemented")
        LOGGER.error("%s.%s: %s", self.__class__.__name__,
                     inspect.stack()[0][3], str(err))
        raise err

    def get(self, key, value=None):
        """
        Get the given config.

        :param key: The config to be getted, string like "key"
        :param value: The config to be getted, string like "value"
        :returns None: Success
        :returns value: Success, config value string
        :returns Exceptions: Fail, error in _get()
        :raises: None
        """
        try:
            ret = self._get(key, value)
            if ret is not None:
                ret = ret.replace('\n', ' ').strip()
        except Exception as err:
            if self._user == "UT":
                raise err
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            return err
        return ret

    def _get(self, key, value):
        """
        The inner method to get config.
        The sub class should implement this method.

        :param key: The config key
        :param value: The config value
        :returns None: Success
        :returns value: Success, config value string
        :raises Exceptions: Fail, with info
        """
        err = NotImplementedError("_get method is not implemented")
        LOGGER.error("%s.%s: %s", self.__class__.__name__,
                     inspect.stack()[0][3], str(err))
        raise err

    @staticmethod
    def _getcfg(para):
        """
        Get the the key and value from the config string.

        :param para: The config string
        :returns list: Success, e.g. ["key", "value" or None]
        :raises Exceptions: Error, unexpected errors
        """
        cfg = para.split("=", 1)
        for i, _ in enumerate(cfg):
            cfg[i] = cfg[i].strip()
        if len(cfg) == 1:
            cfg.append(None)
        return cfg

    @staticmethod
    def check(config1, config2):
        """
        Check whether the given configs are the same.

        :param config1: The 1st config value string
        :param config2: The 2nd config value string
        :returns True: Same
        :returns False: Different
        :raises: None
        """
        return config1 == config2

    def _backup(self, config, _):
        """
        The inner method to backup config.
        The sub class should implement this method if needed.

        :param config: The config
        :param rollback_info: The additional info for rollback, mostly a path
        :returns value: Success, config info
        :raises Exceptions: Fail, with info
        """
        cfg = self._getcfg(config)
        val = self._get(cfg[0], cfg[1]).replace('\n', ' ').strip()
        return "{} = {}".format(cfg[0], val)

    def backup(self, config, rollback_info):
        """
        Backup from the given config.

        :param config: The config to be setted, string like "key = value"
        :param rollback_info: The additional info for rollback, mostly a path
        :returns Exceptions: Fail, error in _backup()
        :returns value: Success, config info
        :raises: None
        """
        try:
            ret = self._backup(config, rollback_info)
        except Exception as err:
            if self._user == "UT":
                raise err
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            return err
        return ret

    def _resume(self, key, value):
        """
        The inner method to resume config.
        The sub class should implement this method if needed.

        :param key: The config key
        :param value: The config value
        :returns None: Success
        :returns Exceptions: Fail, error in _set()
        :raises Exceptions: Fail, with info
        """
        if key == "CPI_ROLLBACK_INFO":
            err = NotImplementedError("_resume method is not implemented")
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            raise err
        return self.set("{} = {}".format(key, value))

    def resume(self, config_info):
        """
        Resume from the saved config info.

        :param config_info: The config info to be resumed
        :returns None: Success
        :returns NeedRebootWarning: Success, but need reboot
        :returns SetConfigError: Fail, fail in _resume()
        :returns Exceptions: Fail, error in _resume()
        :raises: None
        """
        cfg = self._getcfg(config_info)
        try:
            ret = self._resume(cfg[0], cfg[1])
        except Exception as err:
            if self._user == "UT":
                raise err
            LOGGER.error("%s.%s: %s", self.__class__.__name__,
                         inspect.stack()[0][3], str(err))
            return err
        return ret


def file_modify(file, start, end, str_content):
    """
    modify the file content
    :param file:  the file needs to be modified
    :param start:  the starting position of the file needs to be modified
    :param end:  the end position of the file needs to be modified
    :param str_content:  the content needs to be modified
    """
    file.seek(0)
    content = file.read()
    if end < start:
        content = content[:start] + str_content + content[start:]
    else:
        content = content[:start] + str_content + content[end + 1:]
    file.seek(0)
    file.truncate()
    file.write(content)


def pre_check(checker=None, file=None, strict=False):
    """
    pre check parameters
    """

    def wrapper(func):
        @wraps(func)
        def prechecked_set(self, key, value):
            if checker is not None:
                try:
                    if file is not None:
                        checker(self, key, value, file)
                    else:
                        checker(self, key, value)
                except TypeError as err:
                    if strict is True:
                        raise err
                except KeyError as err:
                    if strict is True:
                        raise err
                except ValueError as err:
                    raise err
                except Exception as err:
                    if strict is True:
                        raise err
            return func(self, key, value)

        return prechecked_set

    return wrapper
