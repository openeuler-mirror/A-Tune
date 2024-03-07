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
# @Desc      :   load config file and check dependence tools
# #############################################

import os
import time
import getpass
import logging
import subprocess

import paramiko
from global_var import set_value

timestamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
log_file = f'./log/load_config_{timestamp}.log'
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)
logging.getLogger().setLevel(logging.INFO)
logging.info('开始: load_check.py')


def connect_test(pc1, pc2):
    """
    测试pc1与pc2的连通性,使用 ssh 连接
    pc1: {'ip': '', 'user': ''}
    pc2: {'ip': '', 'user': ''}
    """

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # getpass.getpass() 用于隐藏输入的密码
        getpassword = getpass.getpass(f"请输入 {pc2['ip']} 的密码: ")
        logging.info(f'输入密码：********')
        ssh.connect(hostname=pc2['ip'], port=22, username=pc2['user'], password=getpassword)
        logging.info(f'{pc1["ip"]} 与 {pc2["ip"]} 连通性测试成功')
        print(f"{pc1['ip']} 与 {pc2['ip']} 连通性测试成功")
        ssh.close()
    except paramiko.AuthenticationException:
        logging.error(f'{pc1["ip"]} 与 {pc2["ip"]} 连通性测试失败：认证失败')
        print(f"{pc1['ip']} 与 {pc2['ip']} 连通性测试失败：0 认证失败")
    except paramiko.SSHException as e:
        logging.error(f'{pc1["ip"]} 与 {pc2["ip"]} 连通性测试失败：{str(e)}')
        print(f"{pc1['ip']} 与 {pc2['ip']} 连通性测试失败：1 {str(e)}")
    except Exception as e:
        logging.error(f'{pc1["ip"]} 与 {pc2["ip"]} 连通性测试失败：{str(e)}')
        print(f"{pc1['ip']} 与 {pc2['ip']} 连通性测试失败：2 {str(e)}")
    return 1


def host_test_body(data):
    """
    host_test模式: 适用于3台主机的测试模式, 在local上进行pc1与pc2的连通性测试
    data: config/config.json  配置文件
    """
    local = {'ip': '', 'user': ''}  # 本机
    pc1 = {'ip': '', 'user': ''}  # pc1
    pc2 = {'ip': '', 'user': ''}  # pc2

    print("host_test模式: 在 local 上进行 PC1 与 PC2 的交叉验证测试, 请确保 config 文件配置正确, "
          "将在 PC1 上进行性能测试, 请确保 PC1 的项目目录下工具安装正确")
    if not data["host_test"]["local"]["ip"]:
        logging.error(f'文件读取本机 IP 失败，需要用户输入')
        local['ip'] = input("请输入本机 IP: ")
    if not data["host_test"]["local"]["user"]:
        logging.error(f'文件读取本机 User 失败，需要用户输入')
        local['user'] = input("请输入本机用户名: ")
    set_value('HOST_LOCAL_USER', local['user'])
    set_value('HOST_LOCAL_IP', local['ip'])

    if not data["host_test"]["pc1"]["ip"]:
        logging.error(f'文件读取 PC1 IP 失败，需要用户输入')
        pc1['ip'] = input("请输入PC1 IP: ")
    if not data["host_test"]["pc1"]["user"]:
        logging.error(f'文件读取 PC1 User 失败，需要用户输入')
        pc1['user'] = input("请输入 PC1 用户名: ")
    set_value('HOST_PC1_USER', pc1['user'])
    set_value('HOST_PC1_IP', pc1['ip'])

    if not data["host_test"]["pc2"]["ip"]:
        logging.error(f'文件读取 PC2 IP 失败，需要用户输入')
        pc2['ip'] = input("请输入 PC2 IP: ")
    if not data["host_test"]["pc2"]["user"]:
        logging.error(f'文件读取 PC2 User 失败，需要用户输入')
        pc2['user'] = input("请输入 PC2 用户名: ")
    set_value('HOST_PC2_USER', pc2['user'])
    set_value('HOST_PC2_IP', pc2['ip'])

    try:
        connect_test(local, pc1)
        logging.info(f'本机与 PC1 连通性测试成功')
    except ConnectionError:
        logging.error(f'本机与 PC1连通性测试失败')
        print("本机与 PC1 连通性测试失败,请检查网络连接或 config 文件配置")
    try:
        connect_test(local, pc2)
        logging.info(f'本机与 PC2 连通性测试成功')
    except ConnectionError:
        logging.error(f'本机与 PC2 连通性测试失败')
        print("本机与 PC2 连通性测试失败,请检查网络连接或 config 文件配置")
    try:
        connect_test(pc1, pc2)
        logging.info(f' PC1 与 PC2 连通性测试成功')
    except ConnectionError:
        logging.error(f'PC1 与 PC2连通性测试失败')
        print("PC1 与 PC2 连通性测试失败,请检查网络连接或 config 文件配置")
    else:
        logging.error(f'无效的模式选择')
        print("无效的模式选择，请重新选择")


def communication_test_body(data):
    """
    communication_test模式: 2台主机的测试模式, local与remote的连通性测试
    data: config/config.json 配置文件
    """
    if not data["communication_test"]:
        logging.error(f'文件读取 communication_test key 失败，需要用户输入')
        print("文件读取 communication_test key 失败，需要用户输入")

    try:
        local = data['communication_test']['local']
        remote = data['communication_test']['remote']
    except KeyError:
        logging.error(f'文件读取 local or remote 失败，需要用户输入')
        print("文件读取失败，需要用户输入")

    if not data["communication_test"]["local"]["ip"]:
        logging.error(f' 读取本机 ip 失败，需要用户输入')
        local['ip'] = input("请输入本机IP: ")
    if not data["communication_test"]["local"]["user"]:
        logging.error(f'文件读取本机 user 失败，需要用户输入')
        local['user'] = input("请输入本机用户名: ")
    set_value('LOCAL_USER', local['user'])
    set_value('LOCAL_IP', local['ip'])

    if not data["communication_test"]["remote"]["ip"]:
        logging.error(f'文件读取远程主机 ip 失败，需要用户输入')
        remote['ip'] = input("请输入远程主机IP:")
    if not data["communication_test"]["remote"]["user"]:
        logging.error(f'文件读取远程主机 user 失败，需要用户输入')
        remote['user'] = input("请输入远程主机用户名:")
    set_value('REMOTE_USER', remote['user'])
    set_value('REMOTE_IP', remote['ip'])

    try:
        connect_test(local, remote)
    except ConnectionError:
        logging.error(f'本机与远程主机连通性测试失败')
        print("本机与远程主机连通性测试失败,请检查网络连接或 config 文件配置")


def dependence_check():
    """
    检查依赖工具是否存在：UnixBench, netperf
    """
    path = "./tools"
    logging.info(f'检查: UnixBench 工具是否存在')
    if os.path.exists(path + "/byte-unixbench//UnixBench"):
        print("检查UnixBench:存在,满足 CPU 与内存测试依赖")
        logging.info(f'检查: UnixBench 已存在,满足 CPU 与内存测试依赖')
    else:
        print("检查UnixBench: tools 目录下不存在 UnixBench,不满足 CPU 与内存测试依赖")
        logging.error(f'tools 目录下不存在 UnixBench')
        if input("是否下载 UnixBench? (y/n): ") == "y":
            try:
                print("尝试执行命令: cd ./tools && git clone https://github.com/kdlucas/byte-unixbench.git ")
                logging.info(f'尝试下载 UnixBench')
                subprocess.run("cd ./tools && git clone https://github.com/kdlucas/byte-unixbench.git ", check=True)
                print("下载UnixBench成功")
                logging.info(f'下载UnixBench成功')
            except:
                logging.error(f'下载UnixBench失败')
                print(
                    "下载UnixBench失败,请检查网络连接,或访问 https://github.com/kdlucas/byte-unixbench 手动克隆项目至 tools 目录")
                logging.error(f'UnixBench 缺失')
        else:
            print("请手动克隆 UnixBench 至 tools 目录")
            logging.error(f'UnixBench 缺失')
            exit(1)

    print("检查: netperf 工具是否存在")
    if os.path.exists(path + "/netperf"):
        print("检查: netperf 已存在,满足网络测试依赖")
        logging.info(f'netperf 已存在，git版本')
    else:
        cmd = ['yum', 'list', 'installed', '|', 'grep', 'netperf']
        if subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE).returncode == 0:
            print("检查: netperf 已安装,满足网络测试依赖")
            logging.info(f'netperf 已存在，命令行版本')
        else:
            print("tools 目录下不存在 netperf,不满足网络测试依赖")
            if input("是否下载 netperf? (y/n)") == "y":
                try:
                    print("尝试执行命令: git clone https://github.com/HewlettPackard/netperf.git ./tools/")
                    logging.info(f'尝试clone netperf')
                    subprocess.run("/usr/bin/git clone https://github.com/HewlettPackard/netperf.git ./tools/",
                                   check=True)
                    print("下载 netperf 成功")
                    logging.info(f'clone netperf 成功')
                except ConnectionError:
                    logging.error(f'clone netperf 失败')
                    print(
                        "下载 netperf 失败,请检查网络连接,或访问 https://github.com/HewlettPackard/netperf 手动克隆项目至 tools 目录")
            else:
                print("请手动克隆 netperf 至 tools 目录")
                logging.error(f'netperf 缺失')
                exit(1)
