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
# Create: 2020-08-25

"""
Flask application initialization, including log configuration, restful api registration.
"""
import ssl
import logging
from logging.handlers import SysLogHandler
from flask import Flask
from flask_restful import Api


class App:
    """flask application"""

    def __init__(self):
        self.app = Flask(__name__)
        self.app.config.update(SESSION_COOKIE_SECURE=True,
                               SESSION_COOKIE_HTTPONLY=True,
                               SESSION_COOKIE_SAMESITE='Lax')
        self.api = Api(self.app)

    @staticmethod
    def config_log(level):
        """app config log"""
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        logging_format = logging.Formatter('atuned: %(asctime)s [%(levelname)s] '
                                           '%(module)s [%(pathname)s:%(lineno)d] : %(message)s')
        syslog_handler = SysLogHandler(address="/dev/log", facility=SysLogHandler.LOG_LOCAL0)
        syslog_handler.setFormatter(logging_format)

        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.addHandler(syslog_handler)

    def add_resource(self):
        """flask app add resource"""

    def startup_app(self, host, port, tls, cert_file, key_file, ca_file, log_level):
        """start flask app"""
        level = logging.getLevelName(log_level.upper())
        self.config_log(level)
        self.add_resource()
        context = None
        if tls:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=cert_file, keyfile=key_file)
            context.load_verify_locations(ca_file)
            context.verify_mode = ssl.CERT_REQUIRED
        self.app.run(host=host, port=port, ssl_context=context)
