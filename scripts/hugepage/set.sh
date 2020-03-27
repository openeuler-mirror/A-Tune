#!/bin/sh
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

SCRIPT=$(basename $0)

if [ $# != 1 ]; then
  echo "Usage: ${SCRIPT} 0:disable or 1:enable"
  exit 1
fi

PROF_PATH=~/.bash_profile
MYPROF_PATH=~/.bash_tlbprof

HugePages=$(grep HugePages_Total /proc/meminfo | awk '{print $2}')
if [ "${HugePages}" = 0 -o $1 = 0 ]; then
  rm -f ${MYPROF_PATH}
  exit 0
fi

echo "export HUGETLB_MORECORE=yes" >${MYPROF_PATH}
[ $? != 0 ] && exit 2
echo "export LD_PRELOAD=/usr/lib64/libhugetlbfs.so" >>${MYPROF_PATH}
[ $? != 0 ] && exit 2

grep tlbprof ${PROF_PATH} >/dev/null
if [ $? != 0 ]; then
  echo "if [ -f ${MYPROF_PATH} ]; then" >>${PROF_PATH}
  [ $? != 0 ] && exit 3
  echo "  . ${MYPROF_PATH}" >>${PROF_PATH}
  [ $? != 0 ] && exit 3
  echo "fi" >>${PROF_PATH}
  [ $? != 0 ] && exit 3
fi

exit 0

