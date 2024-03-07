#!/usr/bin/bash

# Copyright (c) 2022 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   westtide
# @Contact   :   tocokeo@outlook.com
# @Date      :   2023/10/7
# @License   :   Mulan PSL v2
# @Desc      :   test for load_check
# #############################################
# run 'pytest -p no:logging ./tests/test_load_check.py' under 'multisystem_performance'

import sys
import logging
from unittest import mock

import paramiko
import pytest
from tools.multisystem_performance.src.load_check import connect_test, host_test_body, communication_test_body

sys.path.append("..")
logging.info('开始: test_load_check.py')


class FakeSSHClient:
    """
    创建一个虚拟的 paramiko.SSHClient 类
    """

    def set_missing_host_key_policy(self, policy):
        pass

    def connect(self, hostname, port, username, password):
        pass

    def close(self):
        pass


@pytest.fixture
def fake_ssh_client():
    return FakeSSHClient()


def test_connect_test_successful(fake_ssh_client):
    """
    测试 connect_test 函数的成功情况
    fake_ssh_client: 虚拟的 paramiko.SSHClient 类
    """
    logging.info(f'开始:test_connect_test_successful')
    pc1 = {'ip': '192.168.1.1', 'user': 'user1'}
    pc2 = {'ip': '192.168.1.2', 'user': 'user2'}
    # 使用 unittest.mock.patch 来模拟 getpass.getpass 函数返回密码
    with mock.patch('getpass.getpass', return_value='password'):
        with mock.patch('paramiko.SSHClient', return_value=fake_ssh_client):
            with mock.patch.object(fake_ssh_client, 'connect'):
                result = connect_test(pc1, pc2)
                logging.info(f'result = {result}')
    assert result == 1


def test_connect_test_failure(fake_ssh_client):
    """
    测试 connect_test 函数的认证失败情况
    fake_ssh_client: 虚拟的 paramiko.SSHClient 类
    """
    logging.info(f'开始:test_connect_test_failure')
    pc1 = {'ip': '192.168.1.1', 'user': 'user1'}
    pc2 = {'ip': '192.168.1.2', 'user': 'user2'}
    # 使用 unittest.mock.patch 来模拟 getpass.getpass 函数返回密码
    with mock.patch('getpass.getpass', return_value='wrong_password'):
        with mock.patch('paramiko.SSHClient', return_value=fake_ssh_client):
            with mock.patch.object(fake_ssh_client, 'connect', side_effect=paramiko.AuthenticationException):
                result = connect_test(pc1, pc2)
                logging.info(f'result = {result}')
    assert result == 1


@pytest.fixture
def mock_input(monkeypatch):
    """
    使用 monkeypatch 来模拟 input 函数
    """
    input_values = []

    def mock_input_generator(prompt):
        if input_values:
            return input_values.pop(0)
        else:
            raise ValueError("Not enough input values provided")

    monkeypatch.setattr('builtins.input', mock_input_generator)


def test_host_test_body_missing_config():
    """
    针对 host_test 读取配置文件时缺少配置的情况进行测试
    """
    # 空配置的情况
    data = {}
    # 使用 pytest.raises 检查是否引发了预期的异常
    with pytest.raises(KeyError, match="host_test"):
        host_test_body(data)

    # 包含 host_test 但没有 local的配置
    data = {"host_test": {"pc1": {}, "pc2": {}}}
    with pytest.raises(KeyError, match="local"):
        host_test_body(data)

    # 包含 host_test 和 local 但没有 ip 的配置
    data = {"host_test": {"local": {"user": "testuser"}}}
    with pytest.raises(KeyError, match="ip"):
        host_test_body(data)

    # 包含 host_test 和 local 但没有 pc1 的配置
    data = {"host_test": {"local": {"ip": "127.0.0.1", "user": "testuser"}}}
    with pytest.raises(KeyError, match="pc1"):
        host_test_body(data)


def test_communication_test_body_missing_config():
    """
    针对 communication_test 读取配置文件时缺少配置的情况进行测试
    """
    # 空配置的情况
    data = {}
    with pytest.raises(KeyError, match='communication_test'):
        communication_test_body(data)

    # 包含 communication_test 但没有local的配置
    data = {"communication_test": {"remote": {"ip": "", "user": "remoteuser"}}}
    with pytest.raises(KeyError, match='local'):
        communication_test_body(data)

    # 包含 communication_test 和 local 但没有 ip 的配置
    data = {"communication_test": {"local": {"user": "localuser"}, "remote": {"ip": "", "user": "remoteuser"}}}
    with pytest.raises(KeyError, match='ip'):
        communication_test_body(data)

    # 包含 communication_test 和 local 但没有 remote 的配置
    data = {"communication_test": {"local": {"ip": "192.168.1.1", "user": "localuser"}, }}
    with pytest.raises(KeyError, match='remote'):
        communication_test_body(data)
