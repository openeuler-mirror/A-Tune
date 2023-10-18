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
# @Desc      :   test for get_parameters.py
# #############################################
# run 'pytest -p no:logging ./tests/test_get_parameters.py' under 'multisystem_performance'

import os
import sys
import pytest
import logging
import subprocess

sys.path.append("..")

from unittest.mock import patch, Mock
from tools.multisystem_performance.src.get_parameters import get_os_version, run_command_and_save_result

logging.info('开始: test_get_parameters.py')


def test_get_os_version_exists():
    """
    创建一个虚拟的os-release文件
    tmp_path: 在测试过程中创建临时目录
    """
    # 调用函数并检查返回值
    result = get_os_version()
    output = subprocess.run('cat /etc/os-release', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_text = output.stdout.decode('utf-8').strip('\n')
    if 'openEuler' in output_text:
        assert result == 'openEuler'
    elif 'CentOS' in output_text:
        assert result == 'CentOS'
    else:
        assert result == 'Unknown'


@pytest.fixture
def test_get_os_version_subprocess_run_error(caplog, monkeypatch):
    """
    test_get_os_version_subprocess_run_error: 测试subprocess.run()抛出异常的情况
    caplog: 用于捕获日志
    monkeypatch: 用于模拟subprocess.run()抛出异常
    """

    def mock_subprocess_run(*args, **kwargs):
        raise Exception("Subprocess error")

    # 模拟subprocess.run()抛出异常
    monkeypatch.setattr(subprocess, 'run', mock_subprocess_run)
    result = get_os_version()
    # 断言返回值和日志消息
    assert result == 'Unknown'
    assert "Subprocess error" in caplog.text
    assert "failed: 'cat /etc/os-release',linux_version = Unknown" in caplog.text


@pytest.fixture
def temp_file(tmpdir):
    # 创建临时文件并返回其路径
    temp_file_path = os.path.join(tmpdir, "temp_output.txt")
    yield temp_file_path
    # 清理临时文件
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)


@pytest.fixture
def mock_subprocess():
    with patch('subprocess.Popen') as mock_popen:
        yield mock_popen


def test_run_command_and_save_result(mock_subprocess):
    # 模拟 subprocess.Popen 对象和 communicate 方法的行为
    mock_popen = mock_subprocess.return_value
    process_mock = Mock(returncode=0)
    communicate_mock = Mock()
    communicate_mock.return_value = (b'Command output', b'Command error')
    mock_popen.communicate = communicate_mock
    mock_popen.returncode = process_mock

    cmd = "echo 'test'"
    file_dir = "test_output.txt"

    # 调用被测试的函数
    run_command_and_save_result(cmd, file_dir)

    # 断言命令是否以 shell=True 启动
    mock_subprocess.assert_called_with(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 断言 communicate 方法被调用
    assert communicate_mock.called

    # 断言文件是否被成功保存
    with open(file_dir, 'r') as file:
        content = file.read()
        assert content == 'Command output'

    # 断言命令的返回码是否为 0
    assert process_mock.returncode == 0
