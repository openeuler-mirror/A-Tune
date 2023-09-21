import subprocess
import re
import difflib
import random
import string
from datetime import datetime
import logging

#生成时间戳，用于文件命名
def generate_timestamp_string():
    now = datetime.now()
    timestamp_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    return timestamp_string

timestamp = generate_timestamp_string()


log_file = f'./log/get_sysctl_ulimit_{timestamp}.log'
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)
logging.getLogger().setLevel(logging.INFO)
logging.info('This is a log message')


#获取 linux 版本，CentOS Steam 或者 OpenEuler
def get_os_version():
    linux_version = "Unknown"
    try:
        with open("/etc/os-release", "r") as file:
            for line in file:
                if line.startswith("NAME="):
                    linux_version = line.strip().split("=")[1].strip('"').replace(" ", "")
                    logging.info('获取系统版本为 %s', linux_version, extra={'logfile': log_file})
                    break
    except FileNotFoundError:
        logging.error('failed: \'cat /etc/os-release\' ', extra={'logfile': log_file})
        print("未找到 /etc/os-release 文件，请检查文件是否存在。")
    
    return linux_version

#bash: "syscyl -a" 存储在sysctl@$linux-version$中
def run_sysctl_command_and_save_result(file_name):
    bash_command = "sysctl -a"
    with open(file_name, "w") as output_file:
        process = subprocess.Popen(bash_command, shell=True, stdout=output_file, stderr=subprocess.PIPE)
        _, stderr = process.communicate()
        logging.info('run command \'%s\'', bash_command, extra={'logfile': log_file})
        if process.returncode != 0:
            print(f"命令执行出错：{stderr.decode()}")
            logging.error('failed: run command \'%s\' ', bash_command, extra={'logfile': log_file})

#bash: "ulimit -a" 存储在ulimit@$linux-version$中
def run_ulimit_command_and_save_result(file_name):
    bash_command = "ulimit -a"
    with open(file_name, "w") as output_file:
        process = subprocess.Popen(bash_command, shell=True, stdout=output_file, stderr=subprocess.PIPE)
        _, stderr = process.communicate()
        logging.info('run command \'%s\'', bash_command, extra={'logfile': log_file})
        if process.returncode != 0:
            print(f"命令执行出错：{stderr.decode()}")
            logging.error('failed: run command \'%s\' ', bash_command, extra={'logfile': log_file})

# 执行sysctl -a与ulimit -a命令并保存结果
def run_command_save(sysctl_res_file_name,ulimit_res_file_name):
    # 执行sysctl -a命令并保存结果到sysctl@xxx.txt文件中
    run_sysctl_command_and_save_result("./data/"+sysctl_res_file_name)
    logging.info('run_sysctl_command_and_save_result successfully, save in \'%s\'',"./data/"+sysctl_res_file_name, extra={'logfile': log_file})
    # 执行ulimit -a命令并保存结果到ulimit@xxx.txt文件中
    run_ulimit_command_and_save_result("./data/"+ulimit_res_file_name)
    logging.info('run_ulimit_command_and_save_result successfully, save in \'%s\'',"./data/"+ulimit_res_file_name, extra={'logfile': log_file})

# 使用difflib的比较，保存比较结果diff_result到文件save_difflib_res
def use_differ_res(os_version,sysctl_res_file_name,save_difflib_res):
    # 根据当前操作系统匹配对方的sysctl@xxx文件，使用scp获取对方配置
    file1 = sysctl_res_file_name
    if os_version == "openEuler":
        command = "scp west1@172.22.60.188:~/my_ospp/data/sysctl@CentOSStream.txt ./data/ "
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"执行命令出错：{e}")
        file2 = "sysctl@CentOSStream.txt"
    else:
        command = "scp west2@172.22.60.189:~/my_ospp/data/sysctl@openEuler.txt ./data/ "
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"执行命令出错：{e}")
        file2 = "sysctl@openEuler.txt"    

   # 使用difflib的比较file1与file2的结果
    with open("./data/"+file1) as f1, open("./data/"+file2) as f2:
        logging.info('compare file1 = \'%s\', file2 = \'%s\'',"./data/"+file1,"./data/"+file2, extra={'logfile': log_file})
        text1 = f1.readlines()
        text2 = f2.readlines()
        logging.info('text1 in \'%s\', text2 in \'%s\'',"./data/"+file1, "./data/"+file2,extra={'logfile': log_file})
    diff=difflib.Differ()
    diff_result = diff.compare(text1, text2)
    logging.info('compare file1 and file2 by difflib successfully', extra={'logfile': log_file})   

    #保存比较结果diff_result到文件save_difflib_res
    try:
        with open("./data/"+save_difflib_res, 'w') as file:
            file.write("".join(diff_result))
        logging.info('save diff_result to file \'%s\' successfully', "./data/"+save_difflib_res, extra={'logfile': log_file})
        print(f"比较结果已成功保存到文件: ./data/{save_difflib_res}")
    except IOError:
        logging.error('failed: save diff_result to file \'%s\' ', "./data/"+save_difflib_res, extra={'logfile': log_file})
        print("保存文件时出现错误，请检查路径和文件权限。")



# 显式分析保存比较结果到文件
def analyse_result_to_file(file2lack_dict, file2add_dict, file2modify_dict, file1, file2, file2lack, file2add, file2modify,save_statistical_res):
    result_str = ""
    result_str += "file1: " + file1 + ", file2: " + file2 + " 统计结果为：\n"
    result_str += "file2 缺失的行有: " + str(len(file2lack)) + "行\n"
    result_str += "file2 增加的行有: " + str(len(file2add)) + "行\n"
    result_str += "file2 修改的行有: " + str(len(file2modify)) + "行\n"
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

    try:
        with open("./data/"+save_statistical_res, "w") as file:
            file.write(result_str)
        print("统计结果已成功保存到文件: "+save_statistical_res)
    except IOError:
        print("保存文件时出现错误，请检查路径和文件权限。")





