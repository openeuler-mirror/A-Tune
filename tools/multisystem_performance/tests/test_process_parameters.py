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
# @Desc      :   test for process_parameters.py
# #############################################
# run 'pytest -p no:logging ./tests/test_process_parameters.py' under 'multisystem_performance'

import sys
import logging
import builtins

import pytest
sys.path.append("..")
from tools.multisystem_performance.src.process_parameters import process_parameters, process_differ

logging.info('开始: test_process_parameters.py')


@pytest.fixture
def sample_differ_file_content():
    str = """- Line 1
- Line 2
  Line 3
+ Line 4
- Line 5
+ Line 6
+ Line 7
- Line 8
+ Line 9
  Line 10"""
    return str


def open_mock(filename):
    return filename


def test_process_differ_file_processing(sample_differ_file_content, monkeypatch):
    # 使用 monkeypatch 来模拟内置的 open 函数
    monkeypatch.setattr(builtins, 'open', open_mock)

    # 调用 process_differ 函数
    file2_lack, file2_modify, file2_new = process_differ(None)

    # 检查结果
    assert file2_lack == ["Line 1", "Line 2", "Line 8"]
    assert file2_modify == ["Line 6", "Line 9"]
    assert file2_new == ["Line 4", "Line 7"]