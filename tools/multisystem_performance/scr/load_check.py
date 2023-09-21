from datetime import datetime
import json
import os
import paramiko
import getpass
import logging
import subprocess

#生成时间戳，用于文件命名
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
logging.info('load_config.py start')

# 测试pc1与pc2的连通性
def connect_test(pc1, pc2):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # getpass.getpass() 用于隐藏输入的密码

        getpassword = getpass.getpass(f"请输入 {pc2['ip']} 的密码: ")
        logging.info('请输入 %s 的密码:',{pc2['ip']} , extra={'logfile': log_file})
        # 默认端口号为22
        ssh.connect(hostname=pc2['ip'], port=22, username=pc2['user'], password=getpassword)
        logging.info('%s 与 %s 连通性测试成功', {pc1['ip']}, {pc2['ip']}, extra={'logfile': log_file})
        print(f"{pc1['ip']} 与 {pc2['ip']} 连通性测试成功")
        ssh.close()
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
def host_test_body(data) :

    local = {'ip': '', 'user': ''}  # 本机
    pc1 = {'ip': '', 'user': ''}    # pc1
    pc2 = {'ip': '', 'user': ''}    # pc2
    
    if not data["host_test"]["local"]["ip"]:
        logging.info('本机IP缺失', extra={'logfile': log_file})
        local['ip'] = input("请输入本机IP, 或者直接编辑config.json文件: ")
    if not data["host_test"]["local"]["user"]:
        logging.info('本机用户名缺失', extra={'logfile': log_file})
        local['user']= input("请输入本机用户名, 或者直接编辑config.json文件: ")

    if not data["host_test"]["pc1"]["ip"]:
        logging.info('pc1 IP缺失', extra={'logfile': log_file})
        pc1['ip'] = input("请输入pc1 IP, 或者直接编辑config.json文件:")
    if not data["host_test"]["pc1"]["user"]:
        logging.info('pc1 用户名缺失', extra={'logfile': log_file})
        pc1['user'] = input("请输入pc1 用户名, 或者直接编辑config.json文件: ")
    
    if not data["host_test"]["pc2"]["ip"]:
        logging.info('pc2 IP缺失', extra={'logfile': log_file})
        pc2['ip'] = input("请输入pc2 IP, 或者直接编辑config.json文件: ")
    if not data["host_test"]["pc2"]["user"]:
        logging.info('pc2 用户名缺失', extra={'logfile': log_file})
        pc2['user'] = input("请输入pc2 用户名, 或者直接编辑config.json文件: ")

    try:
        connect_test(local, pc1)
        logging.info('本机与pc1连通性测试成功', extra={'logfile': log_file})
    except Exception as e:
        logging.info('本机与pc1连通性测试失败', extra={'logfile': log_file})
        print("本机与pc1连通性测试失败")
    try:
        connect_test(local, pc2)
        logging.info('本机与pc2连通性测试成功', extra={'logfile': log_file})
    except Exception as e:
        logging.info('本机与pc2连通性测试失败', extra={'logfile': log_file})
        print("本机与pc2连通性测试失败")  
    try:
        connect_test(pc1, pc2)
        logging.info('pc1与pc2连通性测试成功', extra={'logfile': log_file})
    except Exception as e:
        logging.info('pc1与pc2连通性测试失败', extra={'logfile': log_file})
        print("pc1与pc2连通性测试失败")
    else:
        logging.info('无效的模式选择', extra={'logfile': log_file})
        print("无效的模式选择")

# communication_test模式: 2台主机 
def communication_test_body(data):

    local = data['communication_test']['local']
    remote = data['communication_test']['remote']
    if not data["communication_test"]["local"]["ip"]:
        logging.info('0 本机IP缺失', extra={'logfile': log_file})
        local['ip'] = input("请输入本机IP, 或者直接编辑config.json文件: ")
    if not data["communication_test"]["local"]["user"]:
        logging.info('1 本机用户名缺失', extra={'logfile': log_file})
        local['user']= input("请输入本机用户名, 或者直接编辑config.json文件: ")
    if not data["communication_test"]["remote"]["ip"]:
        logging.info('2 远程主机IP缺失', extra={'logfile': log_file})
        remote['ip'] = input("请输入远程主机IP, 或者直接编辑config.json文件: ")
    if not data["communication_test"]["remote"]["user"]:
        logging.info('3 远程主机用户名缺失', extra={'logfile': log_file})
        remote['user'] = input("请输入远程主机用户名, 或者直接编辑config.json文件: ")
    print("本机IP: ", local['ip'])
    print("本机用户名: ", local['user'])
    print("远程主机IP: ", remote['ip'])
    print("远程主机用户名: ", remote['user'])
    connect_test(local, remote)
    logging.info('本机与远程主机连通性测试成功', extra={'logfile': log_file})
    #except Exception as e:
    #    logging.info('本机与远程主机连通性测试失败', extra={'logfile': log_file})
    #    print("本机与远程主机连通性测试失败")


def dependence_check():
    path = "./tools"
    print("检查: UnixBench 工具是否存在")
    if os.path.exists(path+"/byte-unixbench//UnixBench"): 
            print("检查: UnixBench 已存在,满足 CPU 与内存测试依赖")
    else:
        print("tools 目录下不存在 UnixBench,不满足 CPU 与内存测试依赖")
        if input("是否下载 UnixBench? (y/n)") == "y":
            try:
                print("尝试执行命令: cd ./tools && git clone https://github.com/kdlucas/byte-unixbench.git ")
                subprocess.run("cd ./tools && git clone https://github.com/kdlucas/byte-unixbench.git ", check = True)
                print("下载UnixBench成功")
            except:
                print("下载UnixBench失败,请检查网络连接,或访问 https://github.com/kdlucas/byte-unixbench 手动克隆项目至 tools 目录")
        else:
            print("请手动克隆 UnixBench 至 tools 目录")
            exit(1)

    print("检查: netperf 工具是否存在")
    if os.path.exists(path+"/netperf"):
        print("检查: netperf 已存在,满足网络测试依赖")
    else:
        if subprocess.run("yum list installed | grep netperf", shell=True).returncode == 0:
            print("检查: netperf 已安装,满足网络测试依赖")
        else:
            print("tools 目录下不存在 netperf,不满足网络测试依赖")
            if input("是否下载 netperf? (y/n)") == "y":
                try:
                    print("尝试执行命令: git clone https://github.com/HewlettPackard/netperf.git ./tools/")
                    subprocess.run("/usr/bin/git clone https://github.com/HewlettPackard/netperf.git ./tools/", check = True)
                    print("下载 netperf 成功")    
                except:
                    print("下载 netperf 失败,请检查网络连接,或访问 https://github.com/HewlettPackard/netperf 手动克隆项目至 tools 目录")
            else:
                print("请手动克隆 netperf 至 tools 目录")
                exit(1)
    

def change_sysctl_parameters():
    if True:
        input("请按任意键继续...")


def change_ulimit_parameters():
    if True:
        input("请按任意键继续...")

