#!/bin/bash
set -x

cd tpcc
rm -rf mariadb.log
rm -rf slave1.log
rm -rf slave2.log
rm -rf mariadb_tpmc.out

pkill bash
sleep 1
pkill java
sleep 1
ps -ef|grep java
echo 'start runing'

java -cp bin/:lib/mysql-connector-java-5.1.7-bin.jar iomark.TPCCRunner.Master conf/example/mysql/master.properties > mariadb.log 2>&1 &
master_pid=$!
echo "Starting Master..."
sleep 1
java -cp bin/:lib/mysql-connector-java-5.1.7-bin.jar iomark.TPCCRunner.Slave conf/example/mysql/slave1.properties > slave1.log 2>&1 & 
slave1_pid=$!
echo "Starting Slave1..."
sleep 1
java -cp bin/:lib/mysql-connector-java-5.1.7-bin.jar iomark.TPCCRunner.Slave conf/example/mysql/slave2.properties > slave2.log 2>&1 &
slave2_pid=$!
echo "Starting Slave2..."
sleep 1

# 监控 slave1.log
tail -f slave1.log | while read line; do
  if [[ "$line" == *"Terminating users"* ]]; then
    echo "Terminating users at slave1.log detected, killing process..."
    kill $slave1_pid  # 杀死 slave1 进程
    break
  fi
done &  # 将监控放到后台

# 监控 slave2.log
tail -f slave2.log | while read line; do
  if [[ "$line" == *"Terminating users"* ]]; then
    echo "Terminating users at slave2.log detected, killing process..."
    kill $slave2_pid  # 杀死 slave2 进程
    break
  fi
done &  # 将监控放到后台

# 监控 mariadb.log
tail -f mariadb.log | while read line; do
  if [[ "$line" == *"terminate users"* ]]; then
    echo "Terminating users at mariadb1.log detected, killing process..."
    kill $master_pid  # 杀死 master 进程
    break
  fi
done &  # 将监控放到后台

# 等待所有后台任务完成
wait $slave1_pid
wait $slave2_pid
wait $master_pid

total=$(awk '$1 == "average" { total += $3 } END { print total }' mariadb.log)
total=$(printf "%.0f" "$total")

echo $total > mariadb_tpmc.out
