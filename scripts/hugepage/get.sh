#!/bin/sh

MYPROF_PATH=~/.bash_tlbprof

HugePages=`grep HugePages_Total /proc/meminfo | awk '{print $2}'`
if [ ${HugePages} = 0 ]; then
	rm -f ${MYPROF_PATH}
	echo "0" &&	exit 0
fi

[ -f ${MYPROF_PATH} ] && echo "1" && exit 0

echo "0" && exit 0
