#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2020-08-14

"""
The tool to translate file to .yaml files
Usage: python3 translate.py [-h] [-i] [-o] [-t] [-p] [-b] [-n] [-s] [-f]
"""

import argparse
import ast
import os
import glob

from translate_csv2yaml import TranslateCsv2Yaml
from translate_xlsx2yaml import TranslateXlsx2Yaml


def main(in_dir, out_dir, iterations, project_name, block_dev, network_dev, test, file_extension):
    """
    Translate .xlsx or .csv files to .yaml files.
    :param in_dir: the folder of input files.
    :param out_dir: the folder of output yaml files.
    :param iterations: iterations of the project (> 10).
    :param project_name: the name of the configuration project.
    :param block_dev: the name of block device.
    :param network_dev: the name of network device.
    :param test: whether test the commands in file or not.
    :param file_extension: The file extension converted to yaml files.
    :return: None
    """
    if iterations <= 10:
        print(f"Failed: Iterations must be > 10, the input is {iterations}")
        return
    if not os.path.exists(in_dir):
        print(f"Failed: The input directory ({in_dir}) is not existed")
        return
    if not os.path.exists(out_dir):
        print(f"Failed: The output directory ({out_dir}) is not existed")
        return
    if not file_extension in ("xlsx", "csv"):
        print("Failed: The file extension must be be xlsx or csv")
        return

    in_file_list = glob.glob((str(in_dir) + "*." + file_extension))
    if not in_file_list:
        print(f"Warning: No {file_extension} files exist in the directory")
        return

    for file in in_file_list:
        in_file_name = file
        in_file_basename = os.path.basename(file)
        out_file_name = in_file_basename.replace("." + file_extension, ".yaml")
        if os.path.exists(str(out_dir) + out_file_name):
            print(f"Warning: The output yaml file ({out_file_name}) is already exist, overwrite it!--")

        if file_extension == "xlsx":
            translate_yaml = TranslateXlsx2Yaml(os.path.join(in_dir, in_file_name),
                                                os.path.join(out_dir, out_file_name),
                                                project_name, iterations,
                                                block_dev, network_dev, test)
        else:
            translate_yaml = TranslateCsv2Yaml(os.path.join(in_dir, in_file_name),
                                               os.path.join(out_dir, out_file_name),
                                               project_name, iterations,
                                               block_dev, network_dev, test)
        if translate_yaml.translate():
            print(f'Translating {str(file)} SUCCEEDED!')
        else:
            print(f'Translating {str(file)} FAILED!')


if __name__ == '__main__':
    ARG_PARSER = argparse.ArgumentParser(description="translate excel or csv files to yaml files")
    ARG_PARSER.add_argument('-i', '--in_dir', metavar='INPUT DIRECTORY',
                            default="./", help='The folder of input excel or csv files')
    ARG_PARSER.add_argument('-o', '--out_dir', metavar='OUTPUT DIRECTORY',
                            default="./", help='The folder of output yaml files')
    ARG_PARSER.add_argument('-t', '--iteration', metavar='ITERATIONS', type=int,
                            default="100", help='Iterations of the project (> 10)')
    ARG_PARSER.add_argument('-p', '--prj_name', metavar='NAME',
                            default="example", help='The name of the project')
    ARG_PARSER.add_argument('-b', '--block_device', metavar='BLOCK DEVICE',
                            default="sda", help='The name of block device')
    ARG_PARSER.add_argument('-n', '--network_device', metavar='NETWORK DEVICE',
                            default="enp189s0f0", help='The name of network device')
    ARG_PARSER.add_argument('-s', '--test', metavar='TEST COMMAND',
                            type=ast.literal_eval, default=False,
                            help='Whether test the command or not, True or False')
    ARG_PARSER.add_argument('-f', '--file_extension', metavar='FILE EXTENSION',
                            default="csv", help='The file extension converted to yaml files '
                                                'can be xlsx or csv')

    ARGS = ARG_PARSER.parse_args()
    main(ARGS.in_dir, ARGS.out_dir, ARGS.iteration, ARGS.prj_name,
         ARGS.block_device, ARGS.network_device, ARGS.test, ARGS.file_extension)
