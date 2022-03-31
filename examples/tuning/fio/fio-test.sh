#!/bin/sh

FILENAME=""
RW=read
DIRECT=1
SIZE=10G
BLOCKSIZE=4k
NUMJOBS=8
IODEPTH=14
RUNTIME=30


fio -filename=$FILENAME -ioengine=psync -time_based=1 -rw=$RW -direct=$DIRECT  -thread -size=$SIZE -bs=$BLOCKSIZE -numjobs=$NUMJOBS -iodepth=$IODEPTH -runtime=$RUNTIME -lockmem=1G -group_reporting -name=fiotest-`date -d "$current" +%s`

sleep 5
sync
echo 3 > /proc/sys/vm/drop_caches