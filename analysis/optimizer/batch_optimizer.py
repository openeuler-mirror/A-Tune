#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2021-12-03

"""
This class is used to perform batch tuning optimizer
"""

import logging
import sys
import yaml
from analysis.default_config import BATCH_CONFIG_PATH
from analysis.optimizer.optimizer import Optimizer

LOGGER = logging.getLogger(__name__)

class Batch(Optimizer):
    """batch tuning initialize"""

    def __init__(self, name, params, child_conn, prj_name, engine,
                 max_eval=50, sel_feature=False, x0=None, y0=None,
                 n_random_starts=20, split_count=5, noise=0.00001 ** 2,
                 feature_selector="wefs"):
        super().__init__(name, params, child_conn, prj_name, engine, max_eval,
                         sel_feature, x0, y0, n_random_starts, split_count,
                         noise, feature_selector)

    def run(self):
        """start the tuning process"""
        try:
            batch_opt = BatchOptimizer(
                self.knobs, self.child_conn, self.max_eval)
            best_params = batch_opt.batch_minimize_tuning()
            final_param = {"finished": True, "param": best_params}
            self.child_conn.send(final_param)
            return best_params
        except RuntimeError as runtime_error:
            LOGGER.error('Runtime Error: %s', repr(runtime_error))
            self.child_conn.send(runtime_error)
            return None
        except Exception as err:
            LOGGER.error('Unexpected Error: %s', repr(err))
            self.child_conn.send(Exception("Unexpected Error:", repr(err)))
            return None


class BatchOptimizer:
    """Batch tuning manager

    define all candidate configs in /etc/atuned/batch_algo.yaml file, each candidate config defines all the configs
    and the corresponding values.
    e.g., 
    {
        "candidate_config_1": {
            "net.core.netdev_max_backlog": 100000,
            "net.core.rmem_max": 67108864,
            "net.core.somaxconn": 65536,
            "net.core.wmem_max": 8388608,
            "net.ipv4.ip_local_port_range": "32768 60999",
            "net.ipv4.tcp_fin_timeout": 46,
            "net.ipv4.tcp_keepalive_time": 600,
            "net.ipv4.tcp_max_syn_backlog": 262144,
            "net.ipv4.tcp_max_tw_buckets": 1048576, 
            "net.ipv4.tcp_tw_reuse": "0"
        },
        "candidate_config_2": {
            "net.core.netdev_max_backlog": 1000,
            "net.core.rmem_max": 22020096,
            "net.core.somaxconn": 65536,
            "net.core.wmem_max": 1048576,
            "net.ipv4.ip_local_port_range": "32768 60999",
            "net.ipv4.tcp_fin_timeout": 89,
            "net.ipv4.tcp_keepalive_time": 36000,
            "net.ipv4.tcp_max_syn_backlog": 262144,
            "net.ipv4.tcp_max_tw_buckets": 688128,
            "net.ipv4.tcp_tw_reuse": "0"
        }
    }
    """

    def __init__(self, knobs, child_conn, max_eval=100):
        self._search_space = {}

        self._knobs = knobs
        self._child_conn = child_conn
        self._max_eval = max_eval
        self._candidate_configs = {}

    def read_configs(self, file_path):
        """read the configs of batch algorithm from the file_path"""

        with open(file_path, "r") as f:
            configs = yaml.load(f)
        return configs

    def batch_minimize_tuning(self):
        """runing the batch tuning algorithm"""

        try:
            self._candidate_configs = self.read_configs(BATCH_CONFIG_PATH)
        except (IOError, EOFError) as e:
            LOGGER.error('Read file Error: %s', repr(e))
            return None

        def evaluate(config):
            """evalute the performance at each iteration"""

            iter_result = {}

            iter_result["param"] = config
            self._child_conn.send(iter_result)
            result = self._child_conn.recv()
            x_num = 0.0
            eval_list = result.split(',')
            for value in eval_list:
                num = float(value)
                x_num = x_num + num
            performance = x_num
            LOGGER.info('batch tuning: %s, result: %s', config, performance)
            return performance

        best_loss = sys.maxsize - 1
        best_config = None

        for key in self._candidate_configs.keys():

            loss = evaluate(self._candidate_configs[key])

            if loss < best_loss:
                best_loss = loss
                best_config = self._candidate_configs[key]

        return best_config
