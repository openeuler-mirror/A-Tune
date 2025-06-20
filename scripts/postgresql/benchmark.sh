sysbench --db-driver=pgsql --pgsql-host=$1 --pgsql-port=$2 --pgsql-user=$3 --pgsql-password=$4 --pgsql-db=test_64 --tables=10 --table_size=100000 --threads=32 --report-interval=1 oltp_read_write --rand-type=uniform prepare
echo 1 > /tmp/euler-copilot-fifo
sysbench --db-driver=pgsql --pgsql-host=$1 --pgsql-port=$2 --pgsql-user=$3 --pgsql-password=$4 --pgsql-db=test_64 --tables=10 --table_size=100000 --time=180 --threads=32 --report-interval=1 oltp_read_write --rand-type=uniform run
sysbench --db-driver=pgsql --pgsql-host=$1 --pgsql-port=$2 --pgsql-user=$3 --pgsql-password=$4 --pgsql-db=test_64 --tables=10 --table_size=100000 --time=180 --threads=32 --report-interval=1 oltp_read_write --rand-type=uniform cleanup
