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

from datetime import datetime
import os
import paramiko
import getpass
import logging
import subprocess


# 生成时间戳，用于文件命名
def generate_timestamp_string():
    now = datetime.now()
    timestamp_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    return timestamp_string


timestamp = generate_timestamp_string()

log_file = f'./log/load_config_{timestamp}.log'
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)
logging.getLogger().setLevel(logging.INFO)
logging.info('loac_check.py start')


# 测试pc1与pc2的连通性
def connect_test(pc1, pc2):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # getpass.getpass() 用于隐藏输入的密码
        getpassword = getpass.getpass(f"请输入 {pc2['ip']} 的密码: ")
        logging.info('输入密码：********', extra={'logfile': log_file})
        ssh.connect(hostname=pc2['ip'], port=22, username=pc2['user'], password=getpassword)
        logging.info('%s 与 %s 连通性测试成功', {pc1['ip']}, {pc2['ip']}, extra={'logfile': log_file})
        print(f"{pc1['ip']} 与 {pc2['ip']} 连通性测试成功")
    except paramiko.AuthenticationException:
        logging.error('%s 与 %s 连通性测试失败：认证失败', pc1['ip'], pc2['ip'], extra={'logfile': log_file})
        print(f"{pc1['ip']} 与 {pc2['ip']} 连通性测试失败：0 认证失败")
    except paramiko.SSHException as e:
        logging.error('%s 与 %s 连通性测试失败：%s', pc1['ip'], pc2['ip'], str(e), extra={'logfile': log_file})
        print(f"{pc1['ip']} 与 {pc2['ip']} 连通性测试失败：1 {str(e)}")
    except Exception as e:
        logging.error('%s 与 %s 连通性测试失败：%s', pc1['ip'], pc2['ip'], str(e), extra={'logfile': log_file})
        print(f"{pc1['ip']} 与 {pc2['ip']} 连通性测试失败：2 {str(e)}")
    finally:
        ssh.close()


# host_test模式: 3台主机
def host_test_body(data):
    local = {'ip': '', 'user': ''}  # 本机
    pc1 = {'ip': '', 'user': ''}  # pc1
    pc2 = {'ip': '', 'user': ''}  # pc2

    if not data["host_test"]["local"]["ip"]:
        logging.error('文件读取本机 IP 失败，需要用户输入', extra={'logfile': log_file})
        local['ip'] = input("请输入本机 IP: ")
    if not data["host_test"]["local"]["user"]:
        logging.error('文件读取本机 User 失败，需要用户输入', extra={'logfile': log_file})
        local['user'] = input("请输入本机用户名: ")

    if not data["host_test"]["pc1"]["ip"]:
        logging.error('文件读取 PC1 IP 失败，需要用户输入', extra={'logfile': log_file})
        pc1['ip'] = input("请输入PC1 IP: ")
    if not data["host_test"]["pc1"]["user"]:
        logging.error('文件读取 PC1 User 失败，需要用户输入', extra={'logfile': log_file})
        pc1['user'] = input("请输入 PC1 用户名: ")

    if not data["host_test"]["pc2"]["ip"]:
        logging.error('文件读取 PC2 IP 失败，需要用户输入', extra={'logfile': log_file})
        pc2['ip'] = input("请输入 PC2 IP: ")
    if not data["host_test"]["pc2"]["user"]:
        logging.error('文件读取 PC2 User 失败，需要用户输入', extra={'logfile': log_file})
        pc2['user'] = input("请输入 PC2 用户名: ")

    try:
        connect_test(local, pc1)
        logging.info('本机与 PC1 连通性测试成功', extra={'logfile': log_file})
    except Exception:
        logging.error('本机与 PC1连通性测试失败', extra={'logfile': log_file})
        print("本机与 PC1 连通性测试失败,请检查网络连接或 config 文件配置")
    try:
        connect_test(local, pc2)
        logging.info('本机与 PC2 连通性测试成功', extra={'logfile': log_file})
    except Exception:
        logging.error('本机与 PC2 连通性测试失败', extra={'logfile': log_file})
        print("本机与 PC2 连通性测试失败,请检查网络连接或 config 文件配置")
    try:
        connect_test(pc1, pc2)
        logging.info(' PC1 与 PC2 连通性测试成功', extra={'logfile': log_file})
    except Exception:
        logging.error('PC1 与 PC2连通性测试失败', extra={'logfile': log_file})
        print("PC1 与 PC2 连通性测试失败,请检查网络连接或 config 文件配置")
    else:
        logging.error('无效的模式选择', extra={'logfile': log_file})
        print("无效的模式选择，请重新选择")


# communication_test模式: 2台主机
def communication_test_body(data):
    local = data['communication_test']['local']
    remote = data['communication_test']['remote']
    if not data["communication_test"]["local"]["ip"]:
        logging.error('文件读取本机 IP 失败，需要用户输入', extra={'logfile': log_file})
        local['ip'] = input("请输入本机IP: ")
    if not data["communication_test"]["local"]["user"]:
        logging.error('文件读取本机 User 失败，需要用户输入', extra={'logfile': log_file})
        local['user'] = input("请输入本机用户名: ")
    if not data["communication_test"]["remote"]["ip"]:
        logging.error('文件读取远程主机 IP 失败，需要用户输入', extra={'logfile': log_file})
        remote['ip'] = input("请输入远程主机IP:")
    if not data["communication_test"]["remote"]["user"]:
        logging.error('文件读取远程主机 User 失败，需要用户输入', extra={'logfile': log_file})
        remote['user'] = input("请输入远程主机用户名:")
    try:
        connect_test(local, remote)
    except Exception:
        logging.error('本机与远程主机连通性测试失败', extra={'logfile': log_file})
        print("本机与远程主机连通性测试失败,请检查网络连接或 config 文件配置")



def dependence_check():
    path = "./tools"
    print("检查: UnixBench 工具是否存在")
    logging.info('检查: UnixBench 工具是否存在', extra={'logfile': log_file})
    if os.path.exists(path + "/byte-unixbench//UnixBench"):
        print("检查: UnixBench 已存在,满足 CPU 与内存测试依赖")
        logging.info('检查: UnixBench 已存在,满足 CPU 与内存测试依赖', extra={'logfile': log_file})
    else:
        print("tools 目录下不存在 UnixBench,不满足 CPU 与内存测试依赖")
        logging.error('tools 目录下不存在 UnixBench', extra={'logfile': log_file})
        if input("是否下载 UnixBench? (y/n)") == "y":
            try:
                print("尝试执行命令: cd ./tools && git clone https://github.com/kdlucas/byte-unixbench.git ")
                logging.info('尝试下载 UnixBench', extra={'logfile': log_file})
                subprocess.run("cd ./tools && git clone https://github.com/kdlucas/byte-unixbench.git ", check=True)
                print("下载UnixBench成功")
                logging.info('下载UnixBench成功', extra={'logfile': log_file})
            except:
                logging.error('下载UnixBench失败', extra={'logfile': log_file})
                print(
                    "下载UnixBench失败,请检查网络连接,或访问 https://github.com/kdlucas/byte-unixbench 手动克隆项目至 tools 目录")
                logging.error('UnixBench 缺失', extra={'logfile': log_file})
        else:
            print("请手动克隆 UnixBench 至 tools 目录")
            logging.error('UnixBench 缺失', extra={'logfile': log_file})
            exit(1)

    print("检查: netperf 工具是否存在")
    if os.path.exists(path + "/netperf"):
        print("检查: netperf 已存在,满足网络测试依赖")
        logging.info('netperf 已存在，git版本', extra={'logfile': log_file})
    else:
        if subprocess.run("yum list installed | grep netperf", shell=True).returncode == 0:
            print("检查: netperf 已安装,满足网络测试依赖")
            logging.info('netperf 已存在，命令行版本', extra={'logfile': log_file})
        else:
            print("tools 目录下不存在 netperf,不满足网络测试依赖")
            if input("是否下载 netperf? (y/n)") == "y":
                try:
                    print("尝试执行命令: git clone https://github.com/HewlettPackard/netperf.git ./tools/")
                    logging.info('尝试clone netperf', extra={'logfile': log_file})
                    subprocess.run("/usr/bin/git clone https://github.com/HewlettPackard/netperf.git ./tools/",
                                   check=True)
                    print("下载 netperf 成功")
                    logging.info('clone netperf 成功', extra={'logfile': log_file})
                except:
                    logging.error('clone netperf 失败', extra={'logfile': log_file})
                    print(
                        "下载 netperf 失败,请检查网络连接,或访问 https://github.com/HewlettPackard/netperf 手动克隆项目至 tools 目录")
            else:
                print("请手动克隆 netperf 至 tools 目录")
                logging.error('netperf 缺失', extra={'logfile': log_file})
                exit(1)


def change_sysctl_parameters():
    if True:
        input("请按任意键继续...")


def change_ulimit_parameters():
    if True:
        input("请按任意键继续...")
