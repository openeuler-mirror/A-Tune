#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-10-29

"""
Pipe used to send status to golang process.
"""

import os


class NPipe:
    """pipe used to send status to golang process"""

    def __init__(self, pipe_name, pipe_mode=os.O_SYNC | os.O_CREAT | os.O_WRONLY):
        self.pipe = pipe_name
        self.pipe_mode = pipe_mode
        self.file = None

    def write(self, message):
        """write message to file"""
        if not isinstance(message, str):
            return None
        message = message.encode()
        length = os.write(self.file, message)
        return length

    def open(self):
        """open pipe"""
        if not os.path.exists(self.pipe):
            return None
        self.file = os.open(self.pipe, self.pipe_mode)
        return self.file

    def __del__(self):
        self.close()

    def close(self):
        """close file"""
        if not self.file:
            return
        os.close(self.file)


def get_npipe(pipe):
    """get npipe"""
    npipe = NPipe(pipe)
    file = npipe.open()
    if not file:
        return None
    return npipe
