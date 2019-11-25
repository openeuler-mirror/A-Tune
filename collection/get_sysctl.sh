#!/bin/sh

if [ $# -lt 1 ]
then
    echo "Usage: `basename $0` interval"
    exit 1
fi

interval=$1

files=(/proc/sys/kernel/threads-max /proc/sys/fs/file-nr /proc/loadavg)

for file in ${files[@]}
do
    echo -n \"${file}\",
done
echo ""

while :
do
    for file in ${files[@]}
    do
        echo -n \"`cat ${file}`\",
    done
    echo ""
    sleep ${interval}
done
