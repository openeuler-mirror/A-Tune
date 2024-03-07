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
# @Desc      :   get parameters from system
# #############################################

import os
import difflib
import getpass
import logging
import subprocess

import paramiko
from load_check import timestamp
from global_var import set_value, get_value


def get_os_version():
    """
    获取 linux 版本，CentOS Steam 或者 OpenEuler
    """
    logging.info(f'开始: get_os_version')
    linux_version = "Others"
    try:
        output = subprocess.run(['/bin/cat', '/etc/os-release'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_text = output.stdout.decode('utf-8').strip('\n')
        logging.info(f'output = {output} output_text = {output_text}')
        if 'openEuler' in output_text:
            linux_version = 'openEuler'
            logging.info(f'获取当前系统版本为{linux_version}')
        elif 'CentOS' in output_text:
            linux_version = 'CentOS'
            logging.info(f'获取当前系统版本为{linux_version}')
        else:
            linux_version = 'Others'
    except FileNotFoundError:
        logging.error(f'failed: \'cat /etc/os-release\',linux_version = Unknown ')
        print("未找到 /etc/os-release 文件，请检查文件是否存在。")
    return linux_version


def run_command_and_save_result(cmd, file_dir):
    """
    在本地运行 cmd 命令并保存结果到 file_dir
    cod: 命令
    file_dir: 保存结果的路径
    """
    logging.info(f'开始: run_command_and_save_result')
    try:
        with open(file_dir, "w") as output_file:
            process = subprocess.run(cmd, shell=False, stdout=output_file, stderr=subprocess.PIPE)
            logging.info(f'成功:本地运行命令{cmd},保存结果到文件{file_dir}')
            if process.returncode != 0:
                print(f"失败:本地命令执行{cmd}出错,查阅日志获得更多信息")
                logging.error(f'失败: 本地命令执行出错{cmd}出错,错误信息：{process.stderr.decode()} ')
            os.chmod(file_dir, 0o644)
    except Exception as e:
        print(f"发生异常: {e}, 查阅日志获得更多信息")
        logging.error(f'发生异常: {e}, cmd = {cmd}, file_dir = {file_dir}')


def local_run_sys_ulimit_save(sysctl_res_file_name, ulimit_res_file_name):
    """
    执行sysctl -a 与 ulimit -a命令并保存结果, 封装了 run_command_and_save_result
    sysctl_res_file_name: 保存sysctl -a命令结果的文件名：
    ulimit_res_file_name: 保存ulimit -a命令结果的文件名
    """
    logging.info(f'开始: local_run_sys_ulimit_save, sysctl_res_file_name = {sysctl_res_file_name}, '
                 f'ulimit_res_file_name = {ulimit_res_file_name}')
    local_sys_command = ['sysctl', '-a']
    local_ulimit_command = ['ulimit', '-a']
    if sysctl_res_file_name and ulimit_res_file_name:
        run_command_and_save_result(local_sys_command, sysctl_res_file_name)
        run_command_and_save_result(local_ulimit_command, ulimit_res_file_name)


def remote_run_command_and_copy(remote):
    """
    在 remote 主机上执行 sysctl/ulimit 命令，并将结果保存到本机 ./data/{cmd}_{os_version}.txt
    remote: {"user":"xxx","ip":"xxx"}
    """
    logging.info(f'开始: remote_run_command_and_copy')
    if remote is None:
        print("错误: 空参数")
        logging.error(f'失败: remote is None')
        return False

    remote_user = remote["user"]
    remote_ip = remote["ip"]
    os_version = ""

    if not remote_user or not remote_ip:
        print("错误: 空参数")
        logging.error(f'失败: remote_user and remote_ip is None')
        return False

    try:
        # 连接远程主机
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        getpassword = getpass.getpass(f"正在连接: 请输入 {remote_user}@{remote_ip} 的密码: ")
        logging.info(f'密码输入成功，正在连接 {remote_user}@{remote_ip}')
        ssh_client.connect(hostname=remote_ip, username=remote_user, password=getpassword)
        logging.info(f'成功: 连接 {remote_user}@{remote_ip}')

        # 获取remote系统版本
        get_os_cmd = 'cat /etc/os-release'
        stdin, stdout, stderr = ssh_client.exec_command(get_os_cmd)
        output_text = stdout.read().decode('utf-8').strip('\n')
        os_version = 'openEuler' if 'openEuler' in output_text else 'CentOS'
        logging.info(f'成功: 获取 {remote_user}@{remote_ip} 的系统版本为{os_version}')

        cmds = ['sysctl', 'ulimit']
        for cmd in cmds:
            remote_cmd = f'{cmd} -a'
            ssh_client.exec_command('cd ~/A-Tune/tools/multisystem_performance')
            local_file = f'./data/{cmd}@{os_version}-{timestamp}.txt'
            stdin, stdout, stderr = ssh_client.exec_command(remote_cmd)
            logging.info(f'成功: 在 {remote_user}@{remote_ip} 上执行命令{remote_cmd}')
            res = stdout.read().decode('utf-8')
            with open(local_file, 'w') as file:
                file.write(res)
            logging.info('成功: 保存命令结果到本地文件{local_file}')
            print(f'成功:在 {remote_ip} 上获取 {cmd} 参数,保存到本地文件{local_file}')

        ssh_client.close()
    except paramiko.AuthenticationException as auth_exception:
        print(f"身份验证失败: {auth_exception}")
        logging.error(f"身份验证失败: {auth_exception}")
    except paramiko.SSHException as ssh_exception:
        print(f"SSH 连接错误: {ssh_exception}")
        logging.error(f"SSH 连接错误: {ssh_exception}")
        logging.error(f'')
    except Exception as e:
        print(f"发生异常: {e}")
        logging.error(f"发生异常: {e}")
    return os_version


def run_command_and_save_by_mode(mode, data):
    """
    根据 mode 选择模式,在远程执行命令并保存结果到本地,封装了 remote_run_command_and_copy 和 local_run_sys_ulimit_save
    mode: 1-host_test 模式, 2-communication_test 模式
    data: json 配置文件，结构为{"user":"xxx","ip":"xxx"}
    local: 本地保存结果的目录
    """

    logging.info(f'开始: run_command_and_save_by_mode')
    if mode == '1':
        # host_test 模式时，在local上远程控制pc1与pc2, 并将结果保存到./data/{cmd}_{os_version}.txt,返回值为 os_version
        PC1_VERSION = remote_run_command_and_copy(data["host_test"]["pc1"])
        PC2_VERSION = remote_run_command_and_copy(data["host_test"]["pc2"])
        logging.info(f'pc1_version = {PC1_VERSION}, pc2_version = {PC2_VERSION}')
        set_value('PC1_VERSION', PC1_VERSION)
        set_value('PC2_VERSION', PC2_VERSION)

    if mode == '2':
        # Communication_test 模式: 在 local 上远程控制 remote, 并将结果保存到./data/{cmd}_{os_version}.txt,返回值为 os_version
        LOCAL_VERSION = get_os_version()
        set_value('LOCAL_VERSION', LOCAL_VERSION)
        local_sys = f"./data/sysctl@{LOCAL_VERSION}-{timestamp}.txt"
        local_ulimit = f"./data/ulimit@{LOCAL_VERSION}-{timestamp}.txt"
        logging.info(f'local_version = {LOCAL_VERSION},local_sys = {local_sys},local_ulimit = {local_ulimit}')
        if LOCAL_VERSION == 'Others':
            print('本工具暂不支持该系统版本,请使用 CentOS 或 openEuler,继续使用可能出现错误,查阅日志获得更多信息')
            logging.error(f'本工具暂不支持该系统版本,请使用 CentOS 或 openEuler')

        # 保存本地sysctl -a 与 ulimit -a 命令结果
        local_run_sys_ulimit_save(local_sys, local_ulimit)
        # 在local上远程控制remote,并将结果保存到./data/{cmd}_{os_version}.txt
        REMOTE_VERSION = remote_run_command_and_copy(data["communication_test"]["remote"])
        set_value('REMOTE_VERSION', REMOTE_VERSION)
        logging.info(f'remote_version = {REMOTE_VERSION},remote = {data["communication_test"]["remote"]}')


def differ_sysctl_res(mode, save_differ_sysctl_res):
    """
    使用 difflib 比较，保存比较结果 diff_result 到文件 save_differ_sysctl_res
    mode: 1-host_test 模式下读取pc1与pc2的文件
          2-communication_test 模式下读取local与remote的文件
    save_differ_sysctl_res: 指定保存differ结果的文件名
    """

    file1 = ''
    file2 = ""
    logging.info(f'开始: differ_sysctl_res')
    PC1_VERSION = get_value('PC1_VERSION')
    PC2_VERSION = get_value('PC2_VERSION')
    LOCAL_VERSION = get_value('LOCAL_VERSION')
    REMOTE_VERSION = get_value('REMOTE_VERSION')

    if mode == '1':
        # host_test 模式时，比较pc1与pc2的结果，已经存在local上，对比结果仍存在 local 上
        # 只对比 sysctl -a 命令结果
        file1 = f'./data/sysctl@{PC1_VERSION}-{timestamp}.txt'
        file2 = f'./data/sysctl@{PC2_VERSION}-{timestamp}.txt'
        set_value('file1', file1)
        set_value('file2', file2)
        logging.info(f'file1 = {file1}, file2 = {file2}')
    if mode == '2':
        # Communication_test 模式时，比较local与remote的结果，已经存在local上，对比结果仍存在 local 上
        # 只对比 sysctl -a 命令结果
        file1 = f'./data/sysctl@{LOCAL_VERSION}-{timestamp}.txt'
        file2 = f'./data/sysctl@{REMOTE_VERSION}-{timestamp}.txt'
        set_value('file1', file1)
        set_value('file2', file2)
        logging.info(f'file1 = {file1}, file2 = {file2}')
    if not file1 or not file2:
        print("错误: file1 or file2 is None")
        logging.error(f'错误: file1 or file2 is None')

    # 使用 difflib 的比较file1与file2的结果
    with open(file1) as f1, open(file2) as f2:
        logging.info(f'开始: compare file1 = {file1}, file2 = {file2}')
        text1 = f1.readlines()
        text2 = f2.readlines()
        logging.info(f'text1 in {file1}, text2 in {file2}')
    diff = difflib.Differ()
    diff_result = diff.compare(text1, text2)
    logging.info(f'成功: compare file1 and file2 by difflib')

    # 保存比较结果 diff_result 到文件 save_differ_sysctl_res
    try:
        with open(f'./data/{save_differ_sysctl_res}', 'w') as file:
            file.write("".join(diff_result))
            os.chmod(f'./data/{save_differ_sysctl_res}', 0o644)
        print(f'成功: 比较结果已保存到文件: ./data/{save_differ_sysctl_res}')
        logging.info(f'成功: save diff_result to file ./data/{save_differ_sysctl_res}')
    except IOError:
        print('保存文件时出现错误,请检查路径和文件权限,查阅日志获得更多信息')
        logging.error(f'失败: save diff_result to file ./data/{save_differ_sysctl_res}')