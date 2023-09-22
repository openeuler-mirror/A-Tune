from get_parameters import *
from load_check import *
import json


def prgcess_parameters():
    with open('config/config.json') as f:
        data = json.load(f)

    # 选择测试模式
    selected_mode = input("host_test:1 \ncommunication_test):2\n请选择测试模式(1/2):\n")

    if selected_mode == '1':
        host_test_body(data)

    if selected_mode == '2':
        communication_test_body(data)

    else :
        print("无效的模式选择")
        exit(1)


    os_version = get_os_version()
    sysctl_res_file_name = "sysctl@" + os_version + ".txt"
    ulimit_res_file_name = "ulimit@" + os_version + ".txt"
    save_difflib_res = f"differ-{timestamp}.txt"
    save_statistical_res = f"statistical-{timestamp}.txt"
    file2lack = []
    file2modify = []
    file2add = []
    file1=""
    file2=""


    logging.info("sysctl_res_file_name = \'%s\',ulimit_res_file_name = \'%s\',save_difflib_res = \'%s\',save_statistical_res = \'%s\' ",
                sysctl_res_file_name,ulimit_res_file_name,save_difflib_res,save_statistical_res,
                extra={'logfile': log_file})

    run_command_save(sysctl_res_file_name,ulimit_res_file_name)

    use_differ_res(os_version,sysctl_res_file_name,save_difflib_res)

    # 统计比较结果:列表格式

    # 读取比较结果文件
    with open("./data/"+save_difflib_res) as f:
        lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith('-'):
                if lines[i + 2].startswith('-') or lines[i + 2].startswith(' '):
                    file2lack.append(line.strip())
                elif lines[i + 2].startswith('+'):
                    file2modify.append(line.strip())
                elif lines[i + 2].startswith('?'):
                    if lines[i + 4].startswith('+') and lines[i + 6].startswith('?'):
                        #!#
                        file2modify.append(line.strip())
            elif line.startswith('+'):
                file2add.append(line.strip())

    # 统计比较结果:字典格式
    file2lack_dict = {line.strip('-+ \n').split('=', 1)[0]: line.strip('-+ \n').split('=', 1)[1].strip() for line in file2lack}
    file2add_dict = {line.strip('-+ \n').split('=', 1)[0]: line.strip('-+ \n').split('=', 1)[1].strip() for line in file2add}
    file2modify_dict = {line.strip('-+ \n').split('=', 1)[0]: line.strip('-+ \n').split('=', 1)[1].strip() for line in file2modify}

    # 打印统计结果
    print("file1: " + file1 + ", file2: " + file2 + " 统计结果为：")
    print("file2 缺失的行有: " + str(len(file2lack)) + "行")
    print("file2 增加的行有: " + str(len(file2add)) + "行")
    print("file2 修改的行有: " + str(len(file2modify)) + "行")

    # 在原来的代码末尾，添加调用保存结果到文件的函数
    analyse_result_to_file(file2lack_dict, file2add_dict, file2modify_dict, file1, file2, file2lack, file2add, file2modify,save_statistical_res)
