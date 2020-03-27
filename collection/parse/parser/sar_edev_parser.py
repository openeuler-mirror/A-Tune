#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-11-22

"""
The parser to parse the output of sar -n EDEV
"""

from .sar_with_dev_parser import SarWithDevParser


class SarEdevParser(SarWithDevParser):
    """The parser to parse the output of sar -n EDEV"""

    def __init__(self, raw_data_file, data_to_collect, **kwargs):
        """Initialize a sar parser with device. The device field must be the second column.

        @param raw_data_file: the path of raw data
        @param data_to_collect: list of str which represents the metrics to parse
        @param dev_list: list of devices of which metrics whille be collectted
        @param alias: alias name of output fields (default: "saredev")
        """
        SarWithDevParser.__init__(self, raw_data_file, data_to_collect, **kwargs)

    def _get_extra_supported_metrics(self):
        return {"net_sat": ["rxdrop/s", "txdrop/s", "rxfifo/s", "txfifo/s"],
                "err/s": ["rxerr/s", "txerr/s"]}
