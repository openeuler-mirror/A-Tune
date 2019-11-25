#!/bin/sh

if [ $# -lt 1 ]
then
    echo "Usage: `basename $0` interval"
    exit 1
fi

interval=$1
tag=$(date +%Y%m%d-%H%M%S)

awk -F':' '{printf "\"%s\",", $1}' /proc/meminfo
echo ""
while :
do
    awk '{printf "%s,", $2}' /proc/meminfo
    echo ""
    sleep ${interval}
done
