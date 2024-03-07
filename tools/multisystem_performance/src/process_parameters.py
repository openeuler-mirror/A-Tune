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
# @Date      :   2023/9/22
# @License   :   Mulan PSL v2
# @Desc      :   process parameters and save result to file
# #############################################

import os
import json
import logging

from global_var import set_value, get_value
from get_parameters import run_command_and_save_by_mode, differ_sysctl_res
from load_check import host_test_body, communication_test_body, timestamp


def process_differ(data):
    """
    读取比较结果文件,统计比较结果,并保存到文件
    封装了 run_command_and_save_by_mode 和 differ_sysctl_res 两个函数
    data: 读取的配置文件config.json
    """
    PC1_VERSION = get_value('PC1_VERSION')
    PC2_VERSION = get_value('PC2_VERSION')
    LOCAL_VERSION = get_value('LOCAL_VERSION')
    REMOTE_VERSION = get_value('REMOTE_VERSION')

    file2_lack = []
    file2_modify = []
    file2_new = []  # 统计比较结果:列表格式
    save_differ_sysctl_res = f'differ-{timestamp}.txt'  # 保存比较结果的文件名, 参数会被传递到differ_sysctl_res 函数
    save_statistical_res = f'statistical-{timestamp}.txt'  # 保存统计结果的文件名, 参数会被传递到statistical_res 函数

    '''
    根据测试模式选择运行命令 
    host 模式: PC1 与 PC2 的 4 个文件
    communication 模式: local 与 remote 的 4 个文件
    格式: local_file = f'./data/{cmd}@{os_version}-{timestamp}.txt' 应该不会冲突
    '''
    run_command_and_save_by_mode(get_value('SELECTED_MODE'), data)

    '''
    根据测试模式进行 differ 比较
    host 模式: 比较 PC1 与 PC2 的 sysctl
    communication 模式: 比较 local 与 remote 的 sysctl
    根据 timestamp 避免文件冲突
    '''
    differ_sysctl_res(get_value('SELECTED_MODE'), save_differ_sysctl_res)

    # 读取比较结果文件 save_differ_sysctl_res
    try:
        with open(f'./data/{save_differ_sysctl_res}') as f:
            logging.info(f'./data/{save_differ_sysctl_res} as f ')
            lines = f.readlines()
    except FileNotFoundError as e:
        logging.info(f'{e}file not found')

    for i, line in enumerate(lines):
        if line.startswith('-'):
            if lines[i + 2].startswith('-') or lines[i + 2].startswith(' '):
                file2_lack.append(line.strip())
            elif lines[i + 2].startswith('+'):
                file2_modify.append(line.strip())
            elif lines[i + 2].startswith('?'):
                if lines[i + 4].startswith('+') and lines[i + 6].startswith('?'):
                    file2_modify.append(line.strip())
        elif line.startswith('+'):
            file2_new.append(line.strip())

    logging.info(f'file2_lack: {file2_lack}')
    logging.info(f'file2_new: {file2_new}')
    logging.info(f'file2_modify: {file2_modify}')
    # 统计比较结果:字典格式
    file2lack_dict = {line.strip('-+ \n').split('=', 1)[0]: line.strip('-+ \n').split('=', 1)[1].strip() for line in
                      file2_lack}
    file2add_dict = {line.strip('-+ \n').split('=', 1)[0]: line.strip('-+ \n').split('=', 1)[1].strip() for line in
                     file2_new}

    FILE2_MODIFY_DICT = {line.strip('-+ \n').split('=', 1)[0]: line.strip('-+ \n').split('=', 1)[1].strip() for line in
                         file2_modify}
    set_value('FILE2_MODIFY_DICT', FILE2_MODIFY_DICT)

    # 打印统计结果
    print(f'file1:{get_value("file1")}", file2:{get_value("file2")},'
          f'统计结果为: ')
    print("file2 缺失的行有: " + str(len(file2lack_dict)) + "行")
    logging.info(f'file2 缺失的行有: {str(len(file2lack_dict))}行')
    print("file2 增加的行有: " + str(len(file2add_dict)) + "行")
    logging.info(f'file2 增加的行有: {str(len(file2add_dict))}行')
    print("file2 修改的行有: " + str(len(FILE2_MODIFY_DICT)) + "行")
    logging.info(f'file2 修改的行有: {str(len(FILE2_MODIFY_DICT))}行')

    result_str = ""
    result_str += "file1 与 file2 的比较统计结果为：\n"
    result_str += "file2 缺失的行有: " + str(len(file2_lack)) + "行\n"
    result_str += "file2 增加的行有: " + str(len(file2_new)) + "行\n"
    result_str += "file2 修改的行有: " + str(len(file2_modify)) + "行\n"
    result_str += "====================================================================\n"
    result_str += "file2 缺失的行有：\n"
    for k, v in file2lack_dict.items():
        result_str += k + " " + v + "\n"
    result_str += "====================================================================\n"
    result_str += "file2 增加的行有：\n"
    for k, v in file2add_dict.items():
        result_str += k + " " + v + "\n"
    result_str += "====================================================================\n"
    result_str += "file2 修改的行有：\n"
    for k, v in FILE2_MODIFY_DICT.items():
        result_str += k + " " + v + "\n"

    # 保存统计结果到文件
    try:
        with open(f'./data/{save_statistical_res}', "w") as file:
            file.write(result_str)
            os.chmod(f'./data/{save_statistical_res}', 0o644)
        print(f'成功:统计结果已成功保存到文件:{save_statistical_res}')
        logging.info(f'成功:统计结果已成功保存到文件:./data/{save_statistical_res}')
    except IOError:
        print("失败:保存文件时出现错误,请检查路径和文件权限,查阅日志获得更多信息")
        logging.error(f'IOError:保存文件时出现错误,请检查路径和文件权限,查阅日志获得更多信息')


def process_parameters():
    """
    读取配置文件config.json后根据选择的测试模式执行测试连通性,封装了process_differ
    """

    logging.info('开始: process_parameters.py')
    with open('config/config.json') as f:
        data = json.load(f)

    # 选择测试模式

    SELECTED_MODE = input("(1)host_test模式: 支持3台PC, (2)communication_test模式:支持2台PC. 请选择测试模式(1/2):")
    logging.info(f'选择的测试模式为: {SELECTED_MODE}')
    set_value('SELECTED_MODE', SELECTED_MODE)

    if SELECTED_MODE == '1':
        host_test_body(data)
    if SELECTED_MODE == '2':
        communication_test_body(data)
    else:
        print("无效的模式选择,请重新运行程序")
        exit(1)

    process_differ(data)


def process_differ(data):
    """
    读取比较结果文件,统计比较结果,并保存到文件
    封装了 run_command_and_save_by_mode 和 differ_sysctl_res 两个函数
    data: 读取的配置文件config.json
    """

    file2_lack = []
    file2_modify = []
    file2_new = []  # 统计比较结果:列表格式
    save_differ_sysctl_res = f'differ-{timestamp}.txt'  # 保存比较结果的文件名, 参数会被传递到differ_sysctl_res 函数
    save_statistical_res = f'statistical-{timestamp}.txt'  # 保存统计结果的文件名, 参数会被传递到statistical_res 函数
    SELECTED_MODE = get_value('SELECTED_MODE')
    PC1_VERSION = get_value('PC1_VERSION')
    PC2_VERSION = get_value('PC2_VERSION')
    '''
    根据测试模式选择运行命令 
    host 模式: PC1 与 PC2 的 4 个文件
    communication 模式: local 与 remote 的 4 个文件
    格式: local_file = f'./data/{cmd}@{os_version}-{timestamp}.txt' 应该不会冲突
    '''
    run_command_and_save_by_mode(SELECTED_MODE, data)

    '''
    根据测试模式进行 differ 比较
    host 模式: 比较 PC1 与 PC2 的 sysctl
    communication 模式: 比较 local 与 remote 的 sysctl
    根据 timestamp 避免文件冲突
    '''
    differ_sysctl_res(SELECTED_MODE, save_differ_sysctl_res)

    # 读取比较结果文件 save_differ_sysctl_res
    try:
        with open(f'./data/{save_differ_sysctl_res}') as f:
            logging.info(f'./data/{save_differ_sysctl_res} as f ')
            lines = f.readlines()
    except FileNotFoundError as e:
        logging.info(f'{e}file not found')

    for i, line in enumerate(lines):
        if line.startswith('-'):
            if lines[i + 2].startswith('-') or lines[i + 2].startswith(' '):
                file2_lack.append(line.strip())
            elif lines[i + 2].startswith('+'):
                file2_modify.append(line.strip())
            elif lines[i + 2].startswith('?'):
                if lines[i + 4].startswith('+') and lines[i + 6].startswith('?'):
                    file2_modify.append(line.strip())
        elif line.startswith('+'):
            file2_new.append(line.strip())

    logging.info(f'file2_lack: {file2_lack}')
    logging.info(f'file2_new: {file2_new}')
    logging.info(f'file2_modify: {file2_modify}')
    # 统计比较结果:字典格式
    file2lack_dict = {line.strip('-+ \n').split('=', 1)[0]: line.strip('-+ \n').split('=', 1)[1].strip() for line in
                      file2_lack}
    file2add_dict = {line.strip('-+ \n').split('=', 1)[0]: line.strip('-+ \n').split('=', 1)[1].strip() for line in
                     file2_new}
    file2modify_dict = {line.strip('-+ \n').split('=', 1)[0]: line.strip('-+ \n').split('=', 1)[1].strip() for line in
                        file2_modify}

    # 打印统计结果
    print(f'file1:"./data/sysctl@{PC1_VERSION}-{timestamp}.txt", file2:"./data/sysctl@{PC2_VERSION}-{timestamp}.txt",'
          f'统计结果为: ')
    print("file2 缺失的行有: " + str(len(file2lack_dict)) + "行")
    logging.info(f'file2 缺失的行有: {str(len(file2lack_dict))}行')
    print("file2 增加的行有: " + str(len(file2add_dict)) + "行")
    logging.info(f'file2 增加的行有: {str(len(file2add_dict))}行')
    print("file2 修改的行有: " + str(len(file2modify_dict)) + "行")
    logging.info(f'file2 修改的行有: {str(len(file2modify_dict))}行')

    result_str = ""
    result_str += "file1 与 file2 的比较统计结果为：\n"
    result_str += "file2 缺失的行有: " + str(len(file2_lack)) + "行\n"
    result_str += "file2 增加的行有: " + str(len(file2_new)) + "行\n"
    result_str += "file2 修改的行有: " + str(len(file2_modify)) + "行\n"
    result_str += "====================================================================\n"
    result_str += "file2 缺失的行有：\n"
    for k, v in file2lack_dict.items():
        result_str += k + " " + v + "\n"
    result_str += "====================================================================\n"
    result_str += "file2 增加的行有：\n"
    for k, v in file2add_dict.items():
        result_str += k + " " + v + "\n"
    result_str += "====================================================================\n"
    result_str += "file2 修改的行有：\n"
    for k, v in file2modify_dict.items():
        result_str += k + " " + v + "\n"

    # 保存统计结果到文件
    try:
        with open(f'./data/{save_statistical_res}', "w") as file:
            file.write(result_str)
            os.chmod(f'./data/{save_statistical_res}', 0o644)
        print(f'成功:统计结果已成功保存到文件:{save_statistical_res}')
        logging.info(f'成功:统计结果已成功保存到文件:./data/{save_statistical_res}')
    except IOError:
        print("失败:保存文件时出现错误,请检查路径和文件权限,查阅日志获得更多信息")
        logging.error(f'IOError:保存文件时出现错误,请检查路径和文件权限,查阅日志获得更多信息')


