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
translating file to .yaml files
"""

from io import StringIO

from config_attribute import ConfigAttrName, ConfigAttribute


class TranslateYaml:
    """The base class for translating file to .yaml files"""

    def __init__(self, out_file_name, project_name, iterations, block_dev, network_dev, test):
        """
        init TranslateYaml
        :param out_file_name: the folder of output yaml files.
        :param project_name: the name of the configuration project.
        :param iterations: iterations of the project (> 10).
        :param block_dev: the name of block device.
        :param network_dev: the name of network device.
        :param test: whether test the commands in file or not.
        """
        self.out_file = open(out_file_name, 'w', encoding='utf-8')
        self.project_name = project_name
        self.iterations = iterations
        self.block_dev = block_dev
        self.network_dev = network_dev
        self.test = test

    def __del__(self):
        self.out_file.close()

    def get_head(self):
        """
        Generate the header of yaml file.
        :return: string, the header of yaml file.
        """
        fstr = StringIO()
        fstr.write('project:' + ' \"' + self.project_name + '\"' + '\n')
        fstr.write('maxiterations: ' + str(self.iterations) + '\n')
        fstr.write('startworkload: \"\"\n')
        fstr.write('stopworkload: \"\"\n')
        fstr.write('object : \n')
        return fstr.getvalue()

    @staticmethod
    def read_line(reader, line):
        """
        Get a line into list.
        :param reader: the content of the file to be read.
        :param line: the number of line to get.
        :return: list, the yaml object.
        """
        print(reader, line)
        return []

    def translate(self):
        """
        Translate file to yaml.
        :return: True or False, translation result.
        """
        print(self.project_name)

    def write_yaml(self, content, line):
        """
        write content to yaml.
        :param content: the content written to yaml.
        :param line: the line of content.
        :return: True or False, translation result.
        """
        self.out_file.write(self.get_head())
        obj_list = self.read_line(content, line)
        if not obj_list:
            print(f"Empty workbook, stop translating {self.out_file}")
            return False

        while obj_list:
            self.write_config_attr(obj_list)
            line = line + 1
            obj_list = self.read_line(content, line)
        return True

    def write_config_attr(self, obj_list):
        """
        Write config attribute to yaml
        :param obj_list: config attribute
        :return: None
        """
        is_select = obj_list[ConfigAttrName.select.value].strip()
        if is_select == 'yes':
            config_attr = ConfigAttribute(obj_list, self.block_dev, self.network_dev)
            if self.test:
                valid = config_attr.valid_test_attr()
                if not valid:
                    return

            if config_attr.name != '':
                self.out_file.write(str(config_attr))
