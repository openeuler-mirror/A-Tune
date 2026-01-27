host=127.0.0.1
port=3306
user=root
passwd=123456

[[ -n "$1" ]] && host=$1
[[ -n "$2" ]] && port=$2
[[ -n "$3" ]] && user=$3
[[ -n "$4" ]] && passwd=$4

# cleanup
sysbench --db-driver=mysql --mysql-host=$host --mysql-port=$port --mysql-user=$user --mysql-password=$passwd --mysql-db=sbtest --table_size=10000 --tables=10 --time=180 --threads=16 --report-interval=5 oltp_read_write cleanup
# prepare
sysbench --db-driver=mysql --mysql-host=$host --mysql-port=$port --mysql-user=$user --mysql-password=$passwd --mysql-db=sbtest --table_size=10000 --tables=10 --time=180 --threads=16 --report-interval=5 oltp_read_write prepare
# send start signal to copilot
echo 1 > /tmp/euler-copilot-fifo
# run
sysbench --db-driver=mysql --mysql-host=$host --mysql-port=$port --mysql-user=$user --mysql-password=$passwd --mysql-db=sbtest --table-size=10000 --tables=10 --time=180 --threads=16 --report-interval=5 oltp_write_only --events=0 --mysql-storage-engine=innodb --mysql-ignore-errors=1062,1213,1205,1020 --rand-type=uniform --percentile=95 --forced-shutdown=off --db-ps-mode=disable run
# cleanup
sysbench --db-driver=mysql --mysql-host=$host --mysql-port=$port --mysql-user=$user --mysql-password=$passwd --mysql-db=sbtest --table_size=10000 --tables=10 --time=180 --threads=16 --report-interval=5 oltp_read_write cleanup