#!/bin/sh
# name: gm_benchmark.sh
# desc: a script to run graphicsmagick benchmark
filter=Lanczos
OMP_NUM_THREADS=1
taskset -c 0,1

echo "run gm benchmark"
script gmbasic.txt
gm benchmark convert test00.jpg -size 100x100 -resize 50% output00.jpg
exit

echo "run openMP test"
script openMP.txt
export OMP_NUM_THREADS=4
gm benchmark -iterations 100 -stepthreads 1 convert -resize 100x100 -quality 90 +profile "*" test00.jpg outputMP.jpg
exit

echo "run filter test"
script filter.txt
gm convert -filter Lanczos -size 100x100 -resize 50% test00.jpg outputfi.jpg      
gm compare -metric MSE output00.jpg outputfi.jpg
gm compare -metric PSNR output00.jpg outputfi.jpg
exit

echo "run taskset test"
script taskset.txt
taskset -c 0,1,2,3 gm benchmark convert test00.jpg -size 100x100 -resize 50% outputtask.jpg
gm compare -metric MSE output00.jpg outputtask.jpg
gm compare -metric PSNR output00.jpg outputtask.jpg
exit

echo "run final test"
script final.txt
taskset -c 0,1,2,3 gm benchmark convert  -filter Point test00.jpg -size 100x100 -resize 50% outputL.jpg
exit
script mse.txt
gm compare -metric MSE output00.jpg outputL.jpg
exit
ecript psnr.txt
gm compare -metric PSNR output00.jpg outputL.jpg
exit

