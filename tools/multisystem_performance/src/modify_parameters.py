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
# @Desc      :   modify sysctl parameters and ulimit parameters
# #############################################

import re
import json
import logging
import configparser

import paramiko
import subprocess
from getpass import getpass

from load_check import timestamp
from global_var import get_value
from get_parameters import local_run_sys_ulimit_save


def find_key(sysctl_parameters, target):
    """
    find_key 函数用于递归查找 sysctl_parameters 中是否存在 target 键(块)，如果存在则返回对应的值
    sysctl_parameters: 用于查找的字典
    target: 目标键
    返回: result/value or None, 是键/块
    """
    if isinstance(sysctl_parameters, dict):
        for key, value in sysctl_parameters.items():
            if key == target:
                logging.info(f'成功：{target} in sysctl parameters 0')
                return value
            elif isinstance(value, (dict, list)):
                result = find_key(value, target)
                if result is not None:
                    logging.info(f'成功：{target} in sysctl parameters 1')
                    return result
    elif isinstance(sysctl_parameters, list):
        for item in sysctl_parameters:
            result = find_key(item, target)
            if result is not None:
                logging.info(f'成功：{target} in sysctl parameters 2')
                return result
    return None


def modify_ulimit():
    """
    modify_ulimit 函数用于修改 ulimit 参数,读入配置文件modify.conf中的 ulimit 行
    ulimit_section: 配置文件中 ulimit 部分的行，conf 格式
    """
    SELECTED_MODE = get_value('SELECTED_MODE')
    HOST_PC1_USER = get_value('HOST_PC1_USER')
    HOST_PC1_IP = get_value('HOST_PC1_IP')
    HOST_PC2_USER = get_value('HOST_PC2_USER')
    REMOTE_USER = get_value('REMOTE_USER')
    REMOTE_IP = get_value('REMOTE_IP')
    PC2_VERSION = get_value('PC2_VERSION')
    REMOTE_VERSION = get_value('REMOTE_VERSION')
    success = fail = 0
    ulimit_parameters = ['-t', '-f', '-d', '-s', '-c', '-m', '-u', '-n', '-l', '-v', '-x', '-i', '-q', '-e', '-r', '-N']

    logging.info(f'开始: modify ulimit parameters, SELECTED_MODE = {SELECTED_MODE}')
    if SELECTED_MODE == '1':
        ulimit_file_pc2 = f"./data/ulimit@{PC2_VERSION}-{timestamp}.txt"
        logging.info(f'模式={SELECTED_MODE}, 将在 PC1 = {HOST_PC2_USER}@{HOST_PC1_IP} 上修改 ulimit 参数')
        try:
            with open(ulimit_file_pc2, 'r') as f:
                ulimit_section = f.readlines()
            logging.info(f'成功: 读取 ulimit_file_PC2 = {ulimit_file_pc2}')
        except FileNotFoundError as e:
            logging.error(f'e = {e}')
            print(f'错误: 未找到 ulimit_file_PC2 = {ulimit_file_pc2}, 请检查日志')

        commands = []
        for par in ulimit_parameters:
            pattern = r'(^|\s){}'.format(re.escape(par))
            for line in ulimit_section:
                matches = re.findall(pattern, line)
                if matches:
                    value = line.split()[-1]
                    line = line.strip("\n")
                    logging.info(f'{par} is found in {line}, value is {value}')
                    cmd = ['sudo', 'ulimit', f'{par}', f'{value}']
                    commands.append(cmd)
                    logging.info(f'将 cmd = {cmd} 写入 commands')
                    break  # 如果找到了第一个匹配就退出循环

        try:
            # 连接远程主机
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            getpassword = getpass.getpass(f"正在连接: 请输入 {HOST_PC1_USER}@{HOST_PC1_IP} 的密码: ")
            logging.info(f'密码输入成功，正在连接 {HOST_PC1_USER}@{HOST_PC1_IP}')
            ssh_client.connect(hostname=HOST_PC1_IP, username=HOST_PC1_USER, password=getpassword)
            logging.info(f'成功: 连接{HOST_PC1_USER}@{HOST_PC1_IP}')

            for cmd in commands:
                try:
                    process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout = process.stdout
                    stderr = process.stderr
                    success += 1
                    logging.info(f'成功 {success}: 载入参数{cmd}, stdout = {stdout},stderr:{stderr}')
                except subprocess.CalledProcessError as e:
                    fail += 1
                    logging.error(f'失败 {fail}: 载入参数 {cmd}失败, 错误:{e},请查看日志获取具体信息')
            logging.info(f'成功 {success}, 失败 {fail}')
            ssh_client.close()
        except paramiko.AuthenticationException as e:
            print(f"身份验证失败: {e}")
            logging.error(f"身份验证失败: {e}")
        except paramiko.SSHException as e:
            print(f"SSH 连接错误: {e}")
            logging.error(f"SSH 连接错误: {e}")

    if SELECTED_MODE == '2':
        ulimit_file_remote = f"./data/ulimit@{REMOTE_VERSION}-{timestamp}.txt"
        logging.info(f'模式={SELECTED_MODE}, 将在 PC1 = {REMOTE_USER}@{REMOTE_IP} 上修改 ulimit 参数')
        try:
            with open(ulimit_file_remote, 'r') as f:
                ulimit_data = f.readlines()
        except FileNotFoundError as e:
            logging.error(f'ulimit_file_remote = {ulimit_file_remote}, e = {e}')
            print(f'错误: 未找到文件, 请检查日志')

        for par in ulimit_parameters:
            pattern = r'(^|\s){}'.format(re.escape(par))
            for line in ulimit_data:
                matches = re.findall(pattern, line)
                if matches:
                    value = line.split()[-1]
                    line = line.strip("\n")
                    logging.info(f'{par} is found in {line}, value is {value}')
                    cmd = ['sudo', 'ulimit', f'{par}', f'{value}']
                    try:
                        process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        success += 1
                        logging.info(f'成功 {success}: 载入参数{cmd}')
                    except subprocess.CalledProcessError as e:
                        fail += 1
                        logging.error(f'失败 {fail}: 载入参数 {cmd}失败, 错误:{e},请查看日志获取具体信息')
                    break  # 如果找到了第一个匹配就退出循环
        logging.info(f'成功 {success}, 失败 {fail}')
    logging.info(f'结束: modify ulimit parameters, SELECTED_MODE = {SELECTED_MODE}')


def modify_sysctl_by_line(sysctl_single_line_sections):
    """
    sysctl 参数的行修改模式
    """
    logging.info('开始: 使用行模式修改 sysctl 参数 ')
    success = fail = 0
    for key, value in sysctl_single_line_sections.items():
        if key == "sysctl_single_line":
            logging.info(f'跳过: {key} = {value}')
            continue
        try:
            logging.info(f'尝试载入 {key} = {value} 的参数')
            subprocess.run(f'sysctl {key} = {value}', check=True)
            success += 1
            print(f'成功：载入 {key} = {value} 的参数')
            logging.info(f'{success}成功：载入 sysctl {key} = {value} 的参数')
        except subprocess.CalledProcessError as e:
            fail += 1
            logging.error(f'{fail}失败{e}：载入 {key} = {value} 的参数')
    print(f'使用行模式修改 sysctl 参数, 成功：{success} 个, 失败：{fail} 个，请查看日志获取具体信息')
    logging.info(f'载入 sysctl 参数成功 {success} 个, 失败 {fail} 个 请查看日志获取具体信息')


def modify_sysctl_by_block(sysctl_block_sections, sysctl_parameters):
    """
    sysctl 参数的块修改模式,封装run_command函数
    """
    logging.info('开始: Modify sysctl by block')

    HOST_PC1_USER = get_value('HOST_PC1_USER')
    HOST_PC1_IP = get_value('HOST_PC1_IP')
    HOST_PC2_USER = get_value('HOST_PC2_USER')
    REMOTE_USER = get_value('REMOTE_USER')
    REMOTE_IP = get_value('REMOTE_IP')
    PC2_VERSION = get_value('PC2_VERSION')
    REMOTE_VERSION = get_value('REMOTE_VERSION')
    SELECTED_MODE = get_value('SELECTED_MODE')


    if SELECTED_MODE == '1':
        success = fail = 0
        sysctl_file_pc2 = f"./data/sysctl@{PC2_VERSION}-{timestamp}.txt"
        logging.info(f'模式={SELECTED_MODE}, 将在 PC1 = {HOST_PC2_USER}@{HOST_PC1_IP} 上修改 sysctl 参数')
        try:
            with open(sysctl_file_pc2, 'r') as f:
                data = f.readlines()
            logging.info(f'成功: 读取 ulimit_file_PC2 = {sysctl_file_pc2}')
        except FileNotFoundError as e:
            logging.error(f'e = {e}')
            print(f'错误: 未找到 ulimit_file_PC2 = {sysctl_file_pc2}, 请检查日志')

        commands = []
        for category, params in sysctl_block_sections.items():  # 同样需要查找块
            if category == "sysctl_block":                      # 跳过标记块
                logging.info(f'跳过: {category} = {params}')
                continue
            try:
                result = find_key(sysctl_parameters, category)  # 命中的块, 在块内找子参数
                logging.info(f'开始: category = {category}, result = find_key = {result} ')
                if result is not None:
                    for key, _ in result.items():  # 对块的每个参数进行查找
                        flag = 0
                        for line in data:
                            if key in line:
                                tmp = line.strip('\n')
                                cmd = ['sudo', 'sysctl', f'{tmp}']
                                commands.append(cmd)
                                logging.info(f'成功: key = {key}, 将 {cmd} 写入 commands')
                                flag += 1
                                break
                        if flag == 0:
                            logging.error(f'失败: {key} not in {data}')
                else:
                    logging.error(f'错误: category = {category} not in sysctl_parameters.json')
            except KeyError:
                logging.error(f'无效: parameter configuration for {category}')
        logging.info(f'查找sysctl_block_sections块结束')

        try:
            # 连接远程主机
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            getpassword = getpass.getpass(f"正在连接: 请输入 {HOST_PC1_USER}@{HOST_PC1_IP} 的密码: ")
            logging.info(f'密码输入成功，正在连接 {HOST_PC1_USER}@{HOST_PC1_IP}')
            ssh_client.connect(hostname=HOST_PC1_IP, username=HOST_PC1_USER, password=getpassword)
            logging.info(f'成功: 连接{HOST_PC1_USER}@{HOST_PC1_IP}')

            for cmd in commands:
                try:
                    process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout = process.stdout
                    stderr = process.stderr
                    success += 1
                    logging.info(f'成功 {success}: 载入参数{cmd}, stdout = {stdout},stderr:{stderr}')
                except subprocess.CalledProcessError as e:
                    fail += 1
                    logging.error(f'失败 {fail}: 载入参数 {cmd}失败, 错误:{e},请查看日志获取具体信息')

        except paramiko.AuthenticationException as e:
            print(f"身份验证失败: {e}")
            logging.error(f"身份验证失败: {e}")
        except paramiko.SSHException as e:
            print(f"SSH 连接错误: {e}")
            logging.error(f"SSH 连接错误: {e}")


    if SELECTED_MODE == '2':
        logging.info(f'开始: SELECTED_MODE = {SELECTED_MODE}')
        REMOTE_VERSION = get_value('REMOTE_VERSION')
        sysctl_file_remote = f'./data/sysctl@{REMOTE_VERSION}-{timestamp}.txt'
        commands = []

        with open(sysctl_file_remote, 'r') as f:
            data = f.readlines()
        for category, params in sysctl_block_sections.items():  # 查找块
            if category == "sysctl_block":
                logging.info(f'跳过: {category} = {params}')
                continue
            try:
                result = find_key(sysctl_parameters, category)  # 命中的块
                logging.info(f'开始: category = {category}, result = find_key = {result} ')
                if result is not None:
                    for key, _ in result.items():  # 对块的每个参数进行查找
                        flag = 0
                        for line in data:
                            if key in line:
                                tmp = line.strip('\n')
                                cmd = ['sudo', 'sysctl', f'{tmp}']
                                commands.append(cmd)
                                logging.info(f'成功: key = {key}, 将 {cmd} 写入 commands')
                                flag += 1
                                break
                        if flag == 0:
                            logging.error(f'失败: {key} not in {sysctl_file_remote}')
                else:
                    logging.error(f'错误: category = {category} not in sysctl_parameters.json')
            except KeyError:
                logging.error(f'无效: parameter configuration for {category}')
        logging.info(f'查找sysctl_block_sections块结束')
        run_command(commands, 'sysctl block')


def modify_sysctl_by_copyall():
    """
    sysctl 参数的全量修改模式,封装run_command函数
    """
    logging.info('modify sysctl parameters by copy all')
    copy_all = get_value('file2')
    run_command(copy_all, 'sysctl copy all')
    pass


def backup_new_parameters():
    local_run_sys_ulimit_save('backup_new_sysctl', 'backup_new_ulimit')
    logging.info('成功：备份新的参数')


def backup_old_parameters():
    local_run_sys_ulimit_save('backup_old_sysctl', 'backup_old_ulimit')
    logging.info('成功：备份旧的参数')


def run_command(commands, modify_mode):
    """
    run_command 函数用于载入 sysctl 参数
    file_name: 用于载入的文件名
    modify_mode: 修改模式, 用于日志记录
    """
    print(f'开始: 以{modify_mode}模式修改参数')
    logging.info(f'开始: 以{modify_mode}模式修改参数')
    success = fail = index = 0
    for cmd in commands:
        try:
            process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            success += 1
            stdout = process.stdout
            stderr = process.stderr
            logging.info(f'成功 {success}: 载入参数{cmd}, stdout = {stdout},stderr:{stderr}')
        except subprocess.CalledProcessError as e:
            logging.error(f'失败 {fail}: 载入参数 {cmd}失败, 错误:{e},请查看日志获取具体信息')
            fail += 1
        index += 1
    print(f'使用{modify_mode}修改参数: 成功{success}个, 失败{fail}个, 请查看日志获取具体信息')
    logging.info(f'使用{modify_mode}修改参数: 成功{success}个, 失败{fail}个, 请查看日志获取具体信息')


def modify_parameters():
    """
    modify_parameters 函数用于修改参数, 读取配置文件 modify.conf
    """
    logging.info('开始: modify parameters')
    HOST_LOCAL_USER = get_value('HOST_LOCAL_USER')
    HOST_LOCAL_IP = get_value('HOST_LOCAL_IP')
    HOST_PC1_USER = get_value('HOST_PC1_USER')
    HOST_PC1_IP = get_value('HOST_PC1_IP')
    HOST_PC2_USER = get_value('HOST_PC2_USER')
    HOST_PC2_IP = get_value('HOST_PC2_IP')
    LOCAL_USER = get_value('LOCAL_USER')
    LOCAL_IP = get_value('LOCAL_IP')
    REMOTE_USER = get_value('REMOTE_USER')
    REMOTE_IP = get_value('REMOTE_IP')
    PC1_VERSION = get_value('PC1_VERSION')
    PC2_VERSION = get_value('PC2_VERSION')
    LOCAL_VERSION = get_value('LOCAL_VERSION')
    REMOTE_VERSION = get_value('REMOTE_VERSION')
    SELECTED_MODE = get_value('SELECTED_MODE')
    FILE2_MODIFY_DICT = get_value('FILE2_MODIFY_DICT')

    logging.info(
        f'HOST_LOCAL_USER = {HOST_LOCAL_USER}, HOST_LOCAL_IP = {HOST_LOCAL_IP}, HOST_PC1_USER = {HOST_PC1_USER}, HOST_PC1_IP = {HOST_PC1_IP}, HOST_PC2_USER = {HOST_PC2_USER}, HOST_PC2_IP = {HOST_PC2_IP}, LOCAL_USER = {LOCAL_USER}, LOCAL_IP = {LOCAL_IP}, REMOTE_USER = {REMOTE_USER}, REMOTE_IP = {REMOTE_IP}')
    logging.info(
        f'PC1_VERSION = {PC1_VERSION}, PC2_VERSION = {PC2_VERSION}, LOCAL_VERSION = {LOCAL_VERSION}, REMOTE_VERSION = {REMOTE_VERSION}')
    logging.info(f'SELECTED_MODE = {SELECTED_MODE}, FILE2_MODIFY_DICT = {FILE2_MODIFY_DICT}')

    # 用于匹配、查找的 sysctl 参数集合，已分类、标注
    json_file = './config/sysctl_parameters.json'
    with open(json_file, 'r') as f:
        sysctl_parameters = json.load(f)
    logging.info(f'成功导入 json_file: {json_file}')

    # 备份旧参数
    backup_old_parameters()
    logging.info('备份成功')

    # 读取配置文件
    def preserve_case(option):
        return option

    config = configparser.ConfigParser()
    config.optionxform = preserve_case  # 使用常规函数来禁用键名小写转换
    config.read('./config/modify.conf')
    logging.info(f'读取配置文件: {config}')

    # 获取 sysctl 部分的配置项
    sysctl_block_section = config['sysctl_block']
    logging.info(f'sysctl_block_section = {sysctl_block_section}')
    for key, value in sysctl_block_section.items():
        logging.debug("%s: %s", key, value)

    sysctl_copy_all_section = config['sysctl_copy_all']
    logging.info(f'sysctl_copy_all_section = {sysctl_copy_all_section}')
    sysctl_single_line_section = config['sysctl_single_line']
    logging.info(f'sysctl_single_line_section = {sysctl_single_line_section}')
    sys_block, sys_all, sys_single = True, True, True

    # 获取修改 ulimit 的配置项
    if config['ulimit_auto']['ulimit_auto'] == '0':
        logging.info('ulimit 部分为空, 不进行修改')
    elif config['ulimit_auto']['ulimit_auto'] == '1':
        logging.info('开始载入配置项, 修改ul')
        modify_ulimit()
        logging.info('修改 ulimit parameters 结束')

    # 检测冲突、是否启用各种模式
    if sysctl_block_section['sysctl_block'] == '0':
        logging.info('sysctl_block部分为空, 不使用块修改模式')
        sys_block = False
    if sysctl_copy_all_section['sysctl_copy_all'] == '0':
        logging.info('sysctl_copy_all部分为空, 不使用全量修改模式')
        sys_all = False
    if sysctl_single_line_section['sysctl_single_line'] == '0':
        logging.info('sysctl_single_line部分为空, 不使用单项修改模式')
        sys_single = False
    if sys_block and sys_all:
        print('sysctl_block部分和sysctl_copy_all部分同时存在, 请检查/config/modify.conf配置文件, 重启程序')
        logging.error('sysctl_block部分和sysctl_copy_all部分同时存在, 冲突')

    # sysctl 分块模式修改
    if sys_block:
        modify_sysctl_by_block(sysctl_block_section, sysctl_parameters)
        if sys_single:
            # 如果单项修改模式也启用, 则再次执行单项修改
            modify_sysctl_by_line(sysctl_single_line_section)

    #  sysctl 全量修改模式
    if sys_all:
        modify_sysctl_by_copyall()
        if sys_single:
            # 如果单项修改模式也启用, 则再次执行单项修改
            modify_sysctl_by_line(sysctl_single_line_section)

    # 仅使用 sysctl 单项修改模式
    if not sys_block and not sys_all and sys_single:
        modify_sysctl_by_line(sysctl_single_line_section)

    # 备份新参数
    backup_new_parameters()