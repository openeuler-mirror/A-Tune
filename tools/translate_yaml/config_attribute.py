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
Configure attribute in yaml file
"""

import subprocess
from enum import Enum
from io import StringIO
import shlex


class ConfigAttrName(Enum):
    """Enumerate config attribute"""
    name = 0
    desc = 1
    get = 2
    set = 3
    need_restart = 4
    type = 5
    options = 6
    dtype = 7
    scope_min = 8
    scope_max = 9
    step = 10
    items = 11
    select = 12


class ConfigAttribute:
    """config attribute in yaml"""

    def __init__(self, obj_list, block_dev, network_dev):
        self.name = obj_list[ConfigAttrName.name.value].strip()
        self.desc = obj_list[ConfigAttrName.desc.value].strip()
        self.get = obj_list[ConfigAttrName.get.value].strip()
        self.set = obj_list[ConfigAttrName.set.value].strip()
        self.need_restart = obj_list[ConfigAttrName.need_restart.value].strip()
        self.type = obj_list[ConfigAttrName.type.value].strip()
        self.options = obj_list[ConfigAttrName.options.value].strip()
        self.dtype = obj_list[ConfigAttrName.dtype.value].strip()
        self.scope_min = obj_list[ConfigAttrName.scope_min.value].strip()
        self.scope_max = obj_list[ConfigAttrName.scope_max.value].strip()
        self.step = obj_list[ConfigAttrName.step.value].strip()
        self.items = obj_list[ConfigAttrName.items.value].strip()
        self.block_device = block_dev
        self.network_device = network_dev

        replace_map = {'@name': self.name, '@block': self.block_device,
                       '@netdev': self.network_device}
        for key, value in replace_map.items():
            if key in self.get:
                self.get = self.get.replace(key, value)
            if key in self.set:
                self.set = self.set.replace(key, value)

        self.need_restart = self.need_restart.lower()

    def exec_cmd(self, cmd, value):
        """
        Execute the input command
        :param cmd: input command
        :param value: the value used in the command
        :return: True or False, the results of the execution
        """
        if 'echo ' in self.set and '>' in self.set:
            cmd1, cmd2 = cmd.split('>')
            with open(cmd2.strip(), 'w', encoding='utf-8') as file:
                process = subprocess.Popen(shlex.split(cmd1), stdout=file, shell=False)
                process.wait()
                result = str(process.returncode)
        elif 'ifconfig ' in self.set:
            process = subprocess.Popen(shlex.split(cmd), shell=False)
            process.wait()
            result = str(process.returncode)
        elif 'sysctl ' in self.set:
            result = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT,
                                             shell=False).decode().strip()
        else:
            process = subprocess.Popen(shlex.split(cmd), shell=False)
            process.wait()
            result = str(process.returncode)

        cmd_fail = False
        if 'sysctl' in self.set:
            if 'Invalid argument' in result:
                cmd_fail = True
        else:
            if result != '0':
                cmd_fail = True

        if cmd_fail:
            print(f'Warning: {self.name} invalid Value {value}, make sure the value is in valid range.')
            return False
        return True

    def valid_test_attr(self):
        """
        check the command and given attr.
        :return: True or False, check result
        """
        if self.type == 'continuous':
            return True

        get_cmd = self.get
        count = get_cmd.count('|')
        process = None
        if count > 0:
            for cmds in get_cmd.split('|'):
                process = subprocess.Popen(shlex.split(cmds), shell=False, stdout=subprocess.PIPE,
                                           stdin=None if process is None else process.stdout)
        else:
            process = subprocess.Popen(shlex.split(get_cmd), shell=False, stdout=subprocess.PIPE)
        result = process.communicate()
        orig_value = bytes.decode(result[0]).replace('\n', ' ').strip()

        if self.dtype == 'int':
            for value in [self.scope_min, self.scope_max]:
                result = self.valid_test_command(value, orig_value)
                if not result:
                    return False
        elif self.dtype == 'string':
            dis_options = self.options.split(';')
            for option in dis_options:
                option = '\"' + option.strip() + '\"'
                result = self.valid_test_command(option, '\"' + orig_value + '\"')
                if not result:
                    return False
        else:
            print(f"Warning: {self.name} invalid dtype {self.dtype}, only support int and string")
            return False
        return True

    def valid_test_command(self, value, orig_value):
        """
        Test the set command
        :param value: the value used in the set command
        :param orig_value: the result of get command
        :return: True or False, the result of execution set command
        """
        if value == orig_value:
            return True

        cmd = self.set.replace('$value', value)
        result = self.exec_cmd(cmd, value)
        return result

    def __repr__(self):
        fstr = StringIO()
        fstr.write('  -\n')
        fstr.write('    name : \"' + self.name + '\"\n')
        fstr.write('    info :\n')
        fstr.write('        desc : \"' + self.desc + '\"\n')
        fstr.write('        get : \"' + self.get + '\"\n')
        fstr.write('        set : \"' + self.set + '\"\n')
        fstr.write('        needrestart : \"' + self.need_restart + '\"\n')
        fstr.write('        type : \"' + self.type + '\"\n')

        if self.type == 'continuous':
            fstr.write('        scope :\n')
            fstr.write('          - ' + self.scope_min + '\n')
            fstr.write('          - ' + self.scope_max + '\n')
            if self.dtype == 'string':
                fstr.write('        dtype : \"string\"\n')
            else:
                fstr.write('        dtype : \"int\"\n')
        elif self.type == 'discrete':
            if self.dtype == 'string':
                fstr.write('        options :\n')
                dis_options = self.options.split(';')
                for option in dis_options:
                    fstr.write('          - \"' + option.strip() + '\"\n')
                fstr.write('        dtype : \"string\"\n')
            elif self.dtype == 'int':
                fstr.write('        scope :\n')
                fstr.write('          - ' + self.scope_min + '\n')
                fstr.write('          - ' + self.scope_max + '\n')
                fstr.write('        step : ' + self.step + '\n')
                fstr.write('        items : \n')
                if self.items != '':
                    dis_items = self.items.split(';')
                    for item in dis_items:
                        fstr.write('          - ' + item + '\n')
                fstr.write('        dtype : \"int\"\n')
            else:
                print(f"Warning: {self.name} invalid dtype {self.dtype}, only support int and string")
        else:
            print(f"Warning: {self.name} invalid type {self.type}, only support continuous and discrete")

        return fstr.getvalue()
