#!/bin/sh
# name: ffmpeg_benchmark.sh
# desc: a script to run ffmpeg benchmark




threads=1
c:v=libx264
b:v=200000
bufsize=2000000
preset=ultrafast


echo "test ffmpeg's performance of transcoding video"
script -a tran.txt
phoronix-test-suite run pts/ffmpeg-6.0.0
time ffmpeg -i test00.flv -b:v 200000 -threads 4 -bufsize 10000000 -c:v libx264 -preset ultrafast  output.mp4 | tee ffmpeg.log & \
ffmpeg -i test00.flv -i output.mp4 -lavfi ssim=\"stats_file=ssim.log\" -f null - & \
ffmpeg -i test00.flv -i output.mp4 -lavfi psnr=\"stats_file=psnr.log\" -f null - & \
top -p $(pgrep -d, -x ffmpeg) | tee top.log
exit




