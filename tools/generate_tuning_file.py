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
# Create: 2020-10-20

"""
The tool to generate the server yaml files for tuning.
Usage: python3 generate_tuning_file.py
"""
import argparse
import os

import yaml


def main(tuning_yamls_path):
    """
    generate the server yaml files for tuning
    """
    all_tuning_config_yaml = 'tuning_params_all.yaml'
    with open(os.path.join(tuning_yamls_path, all_tuning_config_yaml), 'r', encoding='utf-8') as file:
        all_config = yaml.safe_load(file)
    for path, _, yamls in os.walk(tuning_yamls_path):
        for yaml_file in yamls:
            if yaml_file == all_tuning_config_yaml:
                continue
            with open(os.path.join(path, yaml_file), 'r', encoding='utf-8') as file:
                yaml_config = yaml.safe_load(file)
            for index, value in enumerate(yaml_config['object']):
                for _, val in enumerate(all_config['object']):
                    if val['name'] == value['name']:
                        yaml_config['object'][index] = val
                        break
            with open(os.path.join(path, yaml_file), 'w', encoding='utf-8') as file:
                file.write(yaml.dump(yaml_config, sort_keys=False))


if __name__ == '__main__':
    ARG_PARSER = argparse.ArgumentParser(description="generate the server yaml files for tuning")
    ARG_PARSER.add_argument('-d', '--path', metavar='DATA',
                            default="../tuning/yamls/", help='input init yamls path')
    ARGS = ARG_PARSER.parse_args()
    main(ARGS.path)
