#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v1.
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
# Create: 2019-10-29

"""
Pipe used to send status to golang process.
"""

import os
import time


class NPipe():
    #pipe used to send status to golang process
    def __init__(self, pipe_name, pipe_mode = os.O_SYNC | os.O_CREAT | os.O_WRONLY):
        self.pipe = pipe_name
        self.pipe_mode = pipe_mode
        self.f = None

    def write(self, message):
        print("send message:", self.f, message)
        if not isinstance(message, str):
            return None
        message = message.encode()
        length = os.write(self.f, message)
        return length

    def open(self):
        if not os.path.exists(self.pipe):
            return None
        self.f = os.open(self.pipe, self.pipe_mode)
        return self.f

    def __del__(self):
        self.close()

    def close(self):
        if not self.f:
            return
        os.close(self.f)


def getNpipe(pipe, pipe_mode=None):
    npipe = NPipe(pipe)
    f = npipe.open()
    print(f)
    if not f:
        return None
    else:
        return npipe


if __name__ == "__main__":
    npipe = getNpipe("/tmp/pipe.ipc")
    if not npipe:
        print("pipe is none")
        exit(1)
    npipe.write("just a npipe test")
