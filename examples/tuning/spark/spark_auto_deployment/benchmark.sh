#!/bin/bash
source ~/.bashrc

# benchmark
cd HiBench
bin/workloads/micro/wordcount/prepare/prepare.sh
if [ $? -eq 0 ]; then
    echo "------------ HiBench prepare success ------------" >>./hibench.log
else
    echo "------------ HiBench prepare failed  ------------" >>./hibench.log
    exit
fi
bin/workloads/micro/wordcount/spark/run.sh
if [ $? -eq 0 ]; then
    echo "------------ HiBench benchmark success ------------" >>./hibench.log
else
    echo "------------ HiBench benchmark failed  ------------" >>./hibench.log
    exit
fi
cat report/hibench.report
cd ..