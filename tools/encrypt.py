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
# Create: 2020-12-02

"""
Tools to encrypt password.
"""


import argparse
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def convert_to_base64(value):
    base64_type = base64.b64encode(value)
    return base64_type.decode('utf-8')


def encrypt_code(code):
    files = open("/dev/random", 'rb')
    key = files.read(32)
    iv = files.read(32)
    files.close()

    encrypts = Cipher(algorithms.AES(key), modes.GCM(iv),
                      backend=default_backend()).encryptor()
    res = encrypts.update(code)
    print('pwd: ', convert_to_base64(res))
    print('key: ', convert_to_base64(key))
    print('iv: ', convert_to_base64(iv))


if __name__ == '__main__':
    ARG_PARSER = argparse.ArgumentParser(description='generate encrypt password')
    ARG_PARSER.add_argument('-e', '--encrypt', help='words that need to be encrypted')
    ARGS = ARG_PARSER.parse_args()

    if ARGS.encrypt is not None:
        encrypt_code(ARGS.encrypt.encode('utf-8'))
    else:
        print('Please offer password for encrypt')
