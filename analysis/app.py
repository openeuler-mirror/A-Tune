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
Application initialization, including log configuration, restful api registration.
"""

from flask import Flask
from flask_restful import Api
import os
import sys
from resources import configurator
from resources import monitor
from resources import optimizer
from resources import collector
from resources import classification
from resources import profile
from resources import train

from configparser import ConfigParser
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


app = Flask(__name__)
api = Api(app)

api.add_resource(configurator.Configurator, '/v1/setting' ,'/setting')
api.add_resource(monitor.Monitor, '/v1/monitor' ,'/monitor')
api.add_resource(optimizer.Optimizer, '/v1/optimizer' ,'/v1/optimizer/<string:task_id>')
api.add_resource(collector.Collector, '/v1/collector','/v1/collector')
api.add_resource(classification.Classification, '/v1/classification','/v1/classification')
api.add_resource(profile.Profile, '/v1/profile','/v1/profile')
api.add_resource(train.Training, '/v1/training','/v1/training')


def configLog(level):
    loggingFormat = logging.Formatter('atuned: %(asctime)s [%(levelname)s] %(name)s : %(message)s')
    syslogHandler = SysLogHandler(address="/dev/log", facility=SysLogHandler.LOG_LOCAL0)
    syslogHandler.setFormatter(loggingFormat)
    syslogHandler.setLevel(level)

    rootLogger = logging.getLogger()
    rootLogger.addHandler(syslogHandler)


def main(filename):
    if not os.path.exists(filename):
        print("conf file is not exist")
        return
    config = ConfigParser()
    config.read(filename)

    level = logging.getLevelName(config.get("log", "level").upper())
    configLog(level)
    app.run(host="localhost", port=config.get("server", "rest_port"))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("lack of conf file parameter")
        sys.exit(-1)
    main(sys.argv[1])
