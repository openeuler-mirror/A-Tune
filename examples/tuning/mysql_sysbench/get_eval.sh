i=1
while [ $i -lt 10 ]
do
	sleep $i
	if [ -f "PATH/sysbench_oltp_read_write.log" ] && [ -n "$(cat PATH/sysbench_oltp_read_write.log  | grep 'queries:' | awk -F '(' '{print $2}' | awk -F ' ' '{print $1}')" ]; then
		cat PATH/sysbench_oltp_read_write.log  | grep 'queries:' | awk -F '(' '{print $2}' | awk -F ' ' '{print $1}'
		break
	fi
	i=$((i+1))
done