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
# Create: 2020-07-30

"""
translate .csv file to .yaml files
"""

import csv

from translate_yaml import TranslateYaml


class TranslateCsv2Yaml(TranslateYaml):
    """
    The subclass for translating csv to .yaml files
    """

    def __init__(self, in_file_name, out_file_name, project_name,
                 iterations, block_dev, network_dev, test):
        super().__init__(out_file_name, project_name,
                         iterations, block_dev, network_dev, test)
        with open(in_file_name, encoding='utf-8') as file:
            reader = csv.reader(file)
            self.rows = list(reader)

    @staticmethod
    def read_line(reader, line):
        """
        Get a line from csv into list.
        :param reader: the content of the csv to be read.
        :param line: the number of line to get.
        :return: list, the yaml object.
        """
        obj_list = []
        if line >= len(reader):
            return obj_list

        name_ = reader[line][1]
        if name_ is None or name_.strip() == "":
            return obj_list

        for col in range(1, 14):
            val = reader[line][col]
            if val is None:
                val = ''
            obj_list.append(str(val))

        return obj_list

    def translate(self):
        """
        Translate csv to yaml.
        :return: True or False, translation result.
        """
        line = 1
        return self.write_yaml(self.rows, line)
