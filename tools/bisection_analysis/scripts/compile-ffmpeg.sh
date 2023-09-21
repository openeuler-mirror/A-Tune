#!/bin/bash

# Change directory to the FFmpeg source code directory.
cd ../projects/FFmpeg

# Remove any existing build directory and clean up previous builds.
rm -rf build
make clean

# Check out a specific commit or branch from the FFmpeg repository.
# The desired commit or branch name is provided as an argument ($1).
git checkout $1

# Configure FFmpeg build settings:
#   --prefix=./build   : Set the installation prefix to the 'build' directory.
#   --enable-gpl       : Enable GPL (GNU General Public License) components.
#   --enable-libx264   : Enable the libx264 codec library.
# This prepares FFmpeg for compilation with the specified options.
./configure  --prefix=./build --enable-gpl --enable-libx264

# Compile FFmpeg using multiple CPU cores to speed up the process.
make -j

# Install the compiled FFmpeg binaries and libraries into the 'build' directory.
make install

# Return to the original working directory.
cd -
