num_executors=2
executor_core=2
executor_memory=2g
driver_memory=2g
default_parallelism=50
storageLevel=1
shuffle_partitions=4

sed "s/^hibench.yarn.executor.num.*/hibench.yarn.executor.num\t$num_executors/" -i HiBench/conf/spark.conf
sed "s/^hibench.yarn.executor.cores.*/hibench.yarn.executor.cores\t$executor_core/" -i HiBench/conf/spark.conf
sed "s/^spark.executor.memory.*/spark.executor.memory\t$executor_memory/" -i HiBench/conf/spark.conf
sed "s/^spark.driver.memory.*/spark.driver.memory\t$driver_memory/" -i HiBench/conf/spark.conf
sed "s/^spark.default.parallelism.*/spark.default.parallelism\t$default_parallelism/" -i HiBench/conf/spark.conf
sed "s/^hibench.streambench.spark.storageLevel.*/hibench.streambench.spark.storageLevel\t$storageLevel/" -i HiBench/conf/spark.conf
sed "s/^spark.sql.shuffle.partitions.*/spark.sql.shuffle.partitions\t$shuffle_partitions/" -i HiBench/conf/spark.conf

sh HiBench/bin/workloads/sql/join/spark/run.sh
