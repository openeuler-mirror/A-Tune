#!/bin/bash
cd /home/keb/benchmarksql-5.0/run/;
a=$(cat result.txt |grep tpmC | awk '{ $1=NULL; print $11 }')
echo $a
rm -rf result.txt

