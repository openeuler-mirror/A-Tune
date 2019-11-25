#!/bin/sh

SCRIPT=$(basename $0)
SCRIPT_PATH=$(cd "$(dirname "$0")";pwd)

if [ $# != 1 ]; then
	echo "Usage: ${SCRIPT} on or off"
	exit 1
fi

lsmod | grep prefetch_tunning &> /dev/null
uninstall=$?

case "$1" in
	"on")
		policy=15
		;;
	"off")
		policy=0
		;;
	"reset")
		if [ ${uninstall} = 0 ]; then
			rmmod prefetch_tunning
		fi
		exit 0
		;;
	*)
		exit 2
		;;
esac

if [ ${uninstall} != 0 ]; then
	modprobe prefetch_tunning
	[ $? != 0 ] && exit 3
fi

echo ${policy} > /sys/class/misc/prefetch/policy
[ $? != 0 ] && exit 4

exit 0
