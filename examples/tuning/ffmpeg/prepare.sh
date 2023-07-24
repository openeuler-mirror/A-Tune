#!/bin/sh
# Copyright (c) LiJiajun(lijiajun@isrc.iscas.ac.cn),
# School of Computer & AI, Wuhan University of Technology.
# name: prepare.sh
# desc: a script to deploy ffmpeg 6.0 and Apache bench on openeuler 20.03 sp2
# THIS IS ONLY USED FOR OPENEULER 20.03-LTS-SP2.
# 
#Create: 2023-06-27

echo "install or update dependencies"
yum install yasm nasm pkg-config git hg -y
wget https://pkg-config.freedesktop.org/releases/pkg-config-0.29.2.tar.gz
tar -xvf pkg-config-0.29.2.tar.gz
cd pkg-config-0.29.2
./configure  --with-internal-glib
make -j9
make install
cd
git clone http://git.videolan.org/git/x264.git
cd x264
./configure --enable-shared --enable-static --prefix=/usr
make 
make install
cd
hg clone http://hg.videolan.org/x265
cd x265/build
cmake ../source
make -j8
make install


echo "install phoronix-test-suite"
cd
wget https://github.com/phoronix-test-suite/phoronix-test-suite/archive/v9.8.0.tar.gz -O phoronix-test-suite-9.8.0.tar.gz
tar -zxvf phoronix-test-suite-9.8.0.tar.gz
cd phoronix-test-suite-9.8.0
./install-sh
phoronix-test-suite list-available-tests

echo "download ffmpeg 6.0 source code"
cd
wget https://ffmpeg.org/releases/ffmpeg-6.0.tar.gz

echo "extract source code"
tar -zxvf ffmpeg-6.0.tar.gz

echo "enter source code directory"
cd ffmpeg-6.0

echo "configure compile options"
./configure  --enable-shared --enable-libx264 --enable-gpl --prefix=/usr/local/ffmpeg 

echo "compile and install"
make
make install

echo "add ffmpeg to PATH"
echo "export PATH=/usr/local/ffmpeg/bin:$PATH" >> ~/.bashrc
echo "export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PATH" >> ~/.bashrc
source ~/.bashrc

echo "verify ffmpeg installation"
ffmpeg -version


echo "copy the server yaml file to /etc/atuned/tuning/"
cp $path/ffmpeg_server.yaml /etc/atuned/tuning/
