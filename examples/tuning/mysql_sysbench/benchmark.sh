TABLES={tables}
TABLE_SIZE={table_size}

sysbench --config-file=sysbench_config.cfg oltp_read_write --tables=$TABLES --table-size=$TABLE_SIZE --time=30 prepare

taskset -c 2,3 sysbench --config-file=sysbench_config.cfg oltp_read_write --tables=$TABLES --table-size=$TABLE_SIZE --time=300 --mysql-ignore-errors=8005 run  > sysbench_oltp_read_write.log

sysbench --config-file=sysbench_config.cfg oltp_read_write --tables=$TABLES --table-size=$TABLE_SIZE --mysql-ignore-errors=8005 cleanup