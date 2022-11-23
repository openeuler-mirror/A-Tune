path=$(
  cd "$(dirname "$0")"
  pwd
)
echo "current run path is $path"

num_executors=3
executor_core=3
executor_memory=4g
driver_memory=2g
default_parallelism=50
sql_shuffle_partitions=30

sed "s/^hibench.yarn.executor.num.*/hibench.yarn.executor.num\t$num_executors/" -i /apps/HiBench/conf/spark.conf
sed "s/^hibench.yarn.executor.cores.*/hibench.yarn.executor.cores\t$executor_core/" -i /apps/HiBench/conf/spark.conf
sed "s/^spark.executor.memory.*/spark.executor.memory\t$executor_memory/" -i /apps/HiBench/conf/spark.conf
sed "s/^spark.driver.memory.*/spark.driver.memory\t$driver_memory/" -i /apps/HiBench/conf/spark.conf
sed "s/^spark.default.parallelism.*/spark.default.parallelism\t$default_parallelism/" -i /apps/HiBench/conf/spark.conf
sed "s/^spark.sql.shuffle.partitions.*/spark.sql.shuffle.partitions\t$sql_shuffle_partitions/" -i /apps/HiBench/conf/spark.conf

sh /apps/HiBench/bin/workloads/ml/{program}/spark/run.sh