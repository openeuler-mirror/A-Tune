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
# Create: 2020-07-14

"""
The tool to generate the AI models.
Usage: python3 generate_models.py [-h] [-d] [-m] [-s]
"""
import argparse
import ast
import os
import sys

FILE_PATH = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, FILE_PATH + "/../")
from analysis.optimizer.workload_characterization import WorkloadCharacterization


def main(csv_path, model_path, feature_selection, search):
    """
    generate AI models
    :param csv_path: csv path
    :param model_path: model path
    :param feature_selection: select feature model, default value is False
    :param search: enable the grid search for model train, default value is False
    :return: None
    """
    processor = WorkloadCharacterization(model_path)
    processor.train(csv_path, feature_selection, search)


if __name__ == '__main__':
    ARG_PARSER = argparse.ArgumentParser(description="generate AI models")
    ARG_PARSER.add_argument('-d', '--csv_path', metavar='DATA',
                            default=FILE_PATH + "/../analysis/dataset", help='input csv path')
    ARG_PARSER.add_argument('-m', '--model_path', metavar='MODEL',
                            default=FILE_PATH + "/../analysis/models", help='input model path')
    ARG_PARSER.add_argument('-s', '--select', metavar='SELECT',
                            type=ast.literal_eval, default=False,
                            help='whether feature models to be generate, True or False')
    ARG_PARSER.add_argument('-g', '--search', metavar='SEARCH',
                            default=False, help='wether enable the parameter space search')
    ARGS = ARG_PARSER.parse_args()

    main(ARGS.csv_path, ARGS.model_path, ARGS.select, ARGS.search)
