#!/bin/sh
# Copyright (c) 2021 Huawei Technologies Co., Ltd.
#
# The implementation was written so as to confirm atune-adm.
#
# A-Tune is licensed under the Mulan PSL v2,
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2021-2-1

for file in `ls .`
do
  if [[ $file == test_* ]]; then
    sh $file
    if [[ $? != 0 ]]; then
      echo "====== failed to exec test case : $file ======"
      exit 1
    fi
  fi
done
echo "======= The test cases are successfully executed. ======="

