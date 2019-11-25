#!/bin/sh

SCRIPT=$(basename $0)
SCRIPT_PATH=$(cd "$(dirname "$0")";pwd)

if [ $# != 0 ]; then
	echo "Usage: ${SCRIPT}"
	exit 1
fi

lsmod | grep prefetch_tunning &> /dev/null
[ $? != 0 ] && echo "reset" && exit 0

policy=$(cat /sys/class/misc/prefetch/policy | awk '{print $2}'| sort -u)
case "$policy" in
	"15")
		echo "on"
		;;
	"0")
		echo "off"
		;;
	*)
		echo "reset"
		;;
esac

exit 0
