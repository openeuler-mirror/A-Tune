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
# @Desc      :   run benchmark of memory, cpu, disk, net
# #############################################

import os
import json
import logging
import subprocess
import paramiko
import getpass
import configparser

from global_var import get_value
from load_check import timestamp


def all_test():
    cmd = ['cd', './tools/byte-unixbench/UnixBench', '&&', './Run']
    print(f'开始执行memory,cpu,disk测试, 请稍等...')
    logging.info(f'开始:memory,cpu and disk 测试')
    try:
        file_path = f'./data/UnixBench_res_output-{timestamp}.txt'
        with open(file_path, "w") as output_file:
            process = subprocess.Popen(cmd, stdout=output_file, stderr=output_file)
            os.chmod(file_path, 0o644)
        print(f"性能测试完成, UnixBench_res_output.txt 文件已生成, 请查看{file_path}")
        logging.info(f'性能测试完成: file_path = {file_path}')
    except Exception as e:
        print(f"性能测试执行失败：{e}, 请检查日志以获得更多信息")
        logging.error(f"性能测试执行失败：{e}, 请检查日志以获得更多信息")


def tcp_test(ip):
    cmd = ['netperf', '-H', f'{ip}', '-p','12865', '-l', '60']
    print("开始执行网络测试: TCP 吞吐量, 预计 60s......")
    logging.info(f'开始执行网络测试: TCP 吞吐量,TCP Test: cmd = {cmd}')
    try:
        process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f'TCP 测试结果为: {process.stdout.decode()}')
        logging.info(f'TCP 测试结果 = {process.stdout.decode()}')
        logging.info(f'TCP Test: {cmd} 执行成功')
    except subprocess.CalledProcessError as e:
        print(f"网络测试执行失败：{e}")
        logging.error(f'TCP Test: {cmd} 执行失败')
    except Exception as ex:
        print(f"发生未知错误：{ex}")
        logging.error(f'TCP Test: {cmd} 执行失败')


def net_test():
    if get_value('SELECT_MODE') == '1':
        print(
            "host_test模式: 在 local 上进行 PC1 与 PC2 的交叉验证测试, 将在 PC1 上进行性能测试, 请确保各自项目目录下工具安装正确")
        logging.info(f'开始:net 测试')
        with open(f'./config/config.json', 'r') as f:
            config = json.load(f)
        pc1_ip = config["host_test"]["pc1"]["ip"]
        pc1_user = config["host_test"]["pc1"]["user"]
        pc2_ip = config["host_test"]["pc2"]["ip"]

        tcp_test(pc1_ip)

        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            getpassword = getpass.getpass(f"请输入{pc1_user}@{pc1_ip}密码：")
            logging.info(f'输入{pc1_user}@{pc1_ip}密码：******')
            ssh_client.connect(pc1_ip, username=pc1_user, password=getpassword)

            netperf_command = f"netperf -H {pc2_ip} -p 12865 -l 60"
            stdin, stdout, stderr = ssh_client.exec_command(netperf_command)
            logging.info(f'{stdout}')
            for line in stdout:
                print(line.strip())
            ssh_client.close()
        except paramiko.AuthenticationException:
            print("SSH 认证失败，请检查用户名和密码")
            logging.info(f'SSH 认证失败，请检查用户名和密码 {pc1_user}@{pc1_ip}')
        except paramiko.SSHException as e:
            print(f"SSH 连接错误: {str(e)}")
            logging.info(f'SSH 连接错误: {str(e)}')
        except Exception as ex:
            print(f"发生未知错误: {str(ex)}")
            logging.info(f'发生未知错误: {str(ex)}')

    if get_value('SELECT_MODE')  == '2':
        logging.info(f'开始:net 测试')
        file_path = f'./config/config.json'
        with open(file_path, 'r') as f:
            config = json.load(f)
        pc2_ip = config["communication_test"]["remote"]["ip"]
        logging.info(f'pc2_ip = {pc2_ip}')

        tcp_test(pc2_ip)

    print('结束:net 测试')
    logging.info(f'结束:net 测试')


def extra_test():
    logging.info(f'开始: extra_test')

    def preserve_case(option):
        return option

    # 读取配置文件
    config = configparser.ConfigParser()
    config.optionxform = preserve_case  # 使用常规函数来禁用键名小写转换
    config.read('./config/modify.conf')
    logging.info(f'读取配置文件: {config}')

    # 获取 extra_benchmark 部分的配置项
    if config['extra_benchmark']['extra_benchmark'] == '0':
        logging.info('extra_benchmark 不启用, 不使用额外性能测试')

    if config['extra_benchmark']['extra_benchmark'] == '1':
        logging.info('extra_benchmark启用, 使用额外性能测试')
        for key, value in config['extra_benchmark'].items():
            if not key or not value:
                logging.info(f'key = {key}为空或者 key = {key}为空')
            elif key == 'extra_benchmark':
                continue
            elif key and value:
                try:
                    command = value.split()
                    logging.info(f'{key} = {value}')
                    process = subprocess.Popen(command, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                    stdout = process.stdout.read()
                    stderr = process.stderr.read()
                    if process.stderr != 0:
                        logging.error(
                            f'失败执行{command}:  错误:{stderr},stdout = {stdout}')
                    logging.info(f'成功执行{command}, stdout = {stdout}')
                    print(f'成功执行{command}, 输出: {stdout}')
                except ValueError as e:
                    logging.error(f'e = {e}, value={value}')
                except subprocess.CalledProcessError as e:
                    logging.error(f'e={e}')
                    print(f'执行{value}失败，请查看日志获得更多信息')
                except FileNotFoundError as e:
                    logging.error(f'e={e}, value.split() = {value.split()}, command={command}')


def benchmark():
    logging.info(f'开始:benchmark 测试')
    print("请选择测试类型:(1):memory,cpu and disk (2):net (3):all (4):extra test")
    test_type = input()
    logging.info(f'输入: test_type={test_type}')
    if test_type == '1':
        logging.info(f'开始:test_type {test_type}: memory,cpu and disk')
        all_test()
        logging.info(f'结束:{test_type} test')

    elif test_type == '2':
        logging.info(f'开始:test_type {test_type}: net')
        net_test()
        logging.info(f'结束:{test_type} test')

    elif test_type == '3':
        logging.info(f'开始:test_type {test_type}: all')
        all_test()
        net_test()
        logging.info(f'结束:{test_type} test ')

    elif test_type == '4':
        logging.info(f'开始:test_type {test_type}: all')
        extra_test()
        logging.info(f'结束:{test_type} test ')
    else:
        print(f'输入错误, 请重新输入')
        logging.error(f'输入错误, 请重新输入')
