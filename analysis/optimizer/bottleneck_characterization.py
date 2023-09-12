#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2023-08-22

from analysis.engine.config import EngineConfig
import logging

LOGGER = logging.getLogger(__name__)

class BottleneckCharacterization:
        
    def __init__(self):
        self.cpu_thresholds = {
            'CPU.STAT.util': float(EngineConfig.cpu_stat_util), 
            'CPU.STAT.cutil': float(EngineConfig.cpu_stat_cutil), 
            'PERF.STAT.IPC': float(EngineConfig.perf_stat_ipc)
        }
        self.mem_thresholds = {
            'MEM.BANDWIDTH.Total_Util': float(EngineConfig.mem_bandwidth_total_util), 
            'MEM.VMSTAT.util.swap': float(EngineConfig.mem_vmstat_util_swap), 
            'MEM.VMSTAT.util.cpu': float(EngineConfig.mem_vmstat_util_cpu)
        }
        self.net_quality_thresholds = {
            'NET.STAT.ifutil': float(EngineConfig.net_stat_ifutil), 
            'NET.ESTAT.errs': float(EngineConfig.net_estat_errs)
        }
        self.net_io_thresholds = {
            'NET.STAT.rxkBs': float(EngineConfig.net_stat_rxkbs), 
            'NET.STAT.txkBs': float(EngineConfig.net_stat_txkbs)
        }
        self.disk_io_thresholds = {
            'STORAGE.STAT.util': float(EngineConfig.storage_stat_util)
        }
                
    def search_bottleneck(self, data):
        cpu_exist = self.check_thresholds(data, self.cpu_thresholds, "computational", special_key='PERF.STAT.IPC', special_value=-1)
        mem_exist = self.check_thresholds(data, self.mem_thresholds, "memory")
        net_quality_exist = self.check_thresholds(data, self.net_quality_thresholds, "network quality")
        net_io_exist = self.check_thresholds(data, self.net_io_thresholds, "network I/O")
        disk_io_exist = self.check_thresholds(data, self.disk_io_thresholds, "disk I/O")
        
        return cpu_exist, mem_exist, net_quality_exist, net_io_exist, disk_io_exist
    
    def check_thresholds(self, data, thresholds, bottleneck_type, special_key=None, special_value=None):
        for key, threshold in thresholds.items():
            if (special_key is not None and key == special_key and
                  data[key].mean() != special_value and data[key].mean() < threshold):
                LOGGER.info('There is a %s bottleneck', bottleneck_type)
                return True
            elif data[key].mean() >= threshold:
                LOGGER.info('There is a %s bottleneck', bottleneck_type)
                return True
            
        return False
