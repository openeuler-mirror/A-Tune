#!/usr/bin/python3
#encoding: utf-8
# Copyright (c) 2021 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2021-6-03
#******************************************************************************
# ******************************************************************************/
"""
Initialize openEuler center-repo.The source is from https://repo.openeuler.org
"""
import sys
import argparse
from configparser import ConfigParser

def set_confi(config_file, source_data_file):
    """
    source_data_file文件格式为(SECTION为配置文件的section名称，CONFIGNAME为该section下待修改的配置KEY，CONFIG_VALUE为待修改的值)：
    SECTION__CONFIGNAME=CONFIG_VALUE
    """
    config_data = ConfigParser()
    config_data.read(config_file)

    set_list = []
    with open(source_data_file, 'r') as f:
        for str_line in f.readlines():
            str_line = str_line.strip()
            if str_line:
                section = str_line.split("=")[0].split("__")[0]
                key = str_line.split("=")[0].split("__")[1]
                value = str_line.split("=")[1]
                set_list.append([section, key, value])

    for config in set_list:
        #config_data.set(config[0], config[1], config[2])
        config_data[config[0]][config[1]] = config[2]

    with open(config_file, 'w+') as f:
        config_data.write(f)


def main():
    """
    entrypoint
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, help="config file")
    parser.add_argument("-s", "--source", type=str, help="the source data file")
    args = parser.parse_args()
    set_confi(args.config, args.source)

if __name__ == "__main__":
    sys.exit(main())
