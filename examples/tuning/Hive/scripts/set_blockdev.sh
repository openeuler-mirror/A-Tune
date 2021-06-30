#!/bin/bash

disk=`lsblk -l | grep disk |grep -v 'nvme'| awk '{print $1}' | sed "s/sd//g"`
disk=`echo ${disk} | tr ' ' '\n' | sort | tr '\n' ' '`

for i in $disk
do
    /sbin/blockdev --setra $1 /dev/sd$i
done

