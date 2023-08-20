#!/bin/bash

# 跳转到 FFmpeg 源码目录
cd ../projects/FFmpeg

# 检出特定提交
rm -rf build
make clean
git checkout $1

# 运行编译命令
./configure  --prefix=./build --enable-gpl --enable-libx264
make -j
make install

# 返回到原始目录
cd -
