#!/bin/sh

# Copyright (c) 2023 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.

#############################################
# @Author    :   LiJiajun
# @Contact   :   lijiajun@isrc.iscas.ac.cn
# @Date      :   2023/7/14
# @License   :   Mulan PSL v2
# @Desc      :   GraphicsMagick deployment and tuning script
# #############################################

echo "close the firewall and SELinux"
systemctl stop firewalld.service
systemctl disable firewalld.service
setenforce 0

echo "update system and install some dependencies"
dnf update -y
yum install -y python3-dict2xml python3-flask-restful python3-pandas python3-scikit-optimize python3-xgboost python3-pyyaml tar
yum install -y gcc gcc-c++ make cmake autoconf automake libpng libjpeg libpng-devel libjpeg-devel libpng-devel libpng ghostscript libtiff libtiff-devel freetype freetype-devel giflib-devel giflib

echo "download gm 1.3.40"
wget https://sourceforge.net/projects/graphicsmagick/files/graphicsmagick/1.3.40/GraphicsMagick-1.3.40.tar.gz

echo "extracting gm"
tar -zxvf GraphicsMagick-1.3.40.tar.gz

echo "install gm"
cd GraphicsMagick-1.3.40
./configure --prefix=/usr/local/GraphicsMagick
make  
make install

echo "add gm to PATH"
echo 'export GMAGICK_HOME="/usr/local/GraphicsMagick"' >> /etc/profile.d/gmagick.sh
echo 'export PATH="$GMAGICK_HOME/bin:$PATH"' >> /etc/profile.d/gmagick.sh
echo 'LD_LIBRARY_PATH=$GMAGICK_HOME/lib:$LD_LIBRARY_PATH' >> /etc/profile.d/gmagick.sh
echo 'export LD_LIBRARY_PATH' >> /etc/profile.d/gmagick.sh
echo 'export OMP_NUM_THREADS=4' >> /etc/profile
source /etc/profile.d/gmagick.sh
source /etc/profile


echo "gm version checking"
gm version

echo "install phoronix-test-suite"
cd
wget https://github.com/phoronix-test-suite/phoronix-test-suite/archive/v10.8.4.tar.gz -O phoronix-test-suite-10.8.4.tar.gz
tar -zxvf phoronix-test-suite-10.8.4.tar.gz
cd phoronix-test-suite-10.8.4
./install-sh

echo "pts check"
phoronix-test-suite
phoronix-test-suite install graphics-magick-2.1.0

