压力机（客户端）两台：压力机1（9.82.230.66）、压力机2（9.82.199.187）
测试机（服务端）两台：测试机1（9.82.179.1）、压力机2（9.82.199.161）
# 1.环境准备
## 1.1 下载JDK文件
在两台物理机上执行
JDK下载链接：
https://download.oracle.com/java/21/latest/jdk-21_linux-aarch64_bin.tar.gz
下载后解压到opt目录下
```bash
tar -zxvf jdk-21_linux-aarch64_bin.tar.gz -C /opt/
```
## 1.2 配置临时java环境
```bash
export JAVA_HOME=/opt/jdk-21.0.6
export PATH=$JAVA_HOME/bin:$PATH
```
## 1.3 配置永久java环境（可选）

打开bashrc文件
```bash
vim ~/.bashrc
```
将以下命令追加到文件末尾，并source生效
```bash
export JAVA_HOME=/opt/jdk-21.0.6
export PATH=$JAVA_HOME/bin:$PATH
```
使用source命令使修改生效
```bash
source ~/.bashrc
```

该步骤在两台压力机上都要执行，包括A-Tune源码也需要下载到相同的路径，否则可能无法远程执行另外一台压力机的benchmark。
## 1.4 部署A-Tune环境
部署环境时，需要保证两台压力机上的源代码路径是一致的，下文给出的参考方法是两台压力机都到root目录下克隆仓库，也可以根据实际环境进行路径的更改，但都需要保证两个压力机中代码路径的一致，便于后续远程执行benchmark命令。
具体安装启动方式参考A-Tune README-zh 文档第一节“安装A-Tune”,A-Tune仓库链接：https://gitee.com/openeuler/A-Tune

```bash
yum install -y atune atune-engine
```
加载并启动atuned和atune-engine服务:
```bash
systemctl start atuned
systemctl start atune-engine
```
下载A-Tune源码，具体操作如下
```bash
cd ~
git clone https://gitee.com/openeuler/A-Tune.git
```
进入目录A-Tune/examples/tuning/mariadb_distributed,并为tpcc创建目录
```bash
cd A-Tune/examples/tuning/mariadb_distributed
mkdir tpcc
```

## 1.5 tpcc部署
两台压力机都需要部署，可以在一台压力机上配置完成后拷贝到另一台压力机上的相同路径。
下载链接：
https://master.dl.sourceforge.net/project/tpccruner/TPCCRunner_SRC_V1.00.zip?viasf=1
### 1.5.1 编译
在两台压力机上执行
将压缩包copy到A-Tune/examples/tuning/mariadb_distributed/tpcc目录下，进入A-Tune/examples/tuning/mariadb_distributed/tpcc目录然后执行如下命令
```bash
cd tpcc
unzip TPCCRunner_SRC_V1.00.zip
mkdir log
javac -d bin src/iomark/TPCCRunner/*.java
```
### 1.5.2 修改loader.properties文件
在两台压力机上修改conf/example/mysql/loader.properties文件。
应手动修改对应测试机的ip，一台压力机对应一台测试机。
修改内容如下：
```bash
driver=com.mysql.jdbc.Driver
url=jdbc:mysql://9.82.179.1/hsdb
user=root
#password=huawei
threads=8
warehouses=5
```
### 1.5.3 修改master.properties文件
在两台压力机上修改conf/example/mysql/master.properties
修改内容如下：
```bash
listenPort=27891
slaves=slave1,slave2

runMinutes=5
warmupMinutes=2

newOrderPercent=1
paymentPercent=1
orderStatusPercent=45
deliveryPercent=43
stockLevelPercent=10

newOrderThinkSecond=0
paymentThinkSecond=0
orderStatusThinkSecond=0
deliveryThinkSecond=0
stockLevelThinkSecond=0
```
### 1.5.4 修改slave1.properties文件
在两台压力机上修改conf/example/mysql/slave1.properties
应手动修改对应测试机1的ip
修改内容如下：
```bash
name=slave1
masterAddress=127.0.0.1
masterPort=27891

driver=com.mysql.jdbc.Driver
url=jdbc:mysql://9.82.179.1/hsdb
user=root
#password=huawei
poolSize=120

userCount=100
warehouseCount=500
startWarehouseID=1
```
### 1.5.5 修改slave2.properties文件
在两台压力机上修改conf/example/mysql/slave2.properties
应手动修改对应测试机2的ip
修改内容如下：
```bash
name=slave2
masterAddress=127.0.0.1
masterPort=27891

driver=com.mysql.jdbc.Driver
url=jdbc:mysql://9.82.199.161/hsdb
user=root
#password=huawei
poolSize=120

userCount=100
warehouseCount=500
startWarehouseID=1
```


## 1.6 安装mariadb数据库
在两台测试机上安装数据库mariadb
```bash
yum install mariadb -y 
yum install mariadb-server -y
```
## 1.7 配置数据库免密登录
修改/etc/my.cnf文件，在[mysqld]后添加skip-grant-tables（登录时跳过权限检查）
```bash
skip-grant-tables
```
## 1.8 写入数据

在两台测试机上执行，下载TPCCRunner_SRC_V1.00.zip压缩包，解压后，在数据库中创建数据
```bash
mysql -uroot -vvv -n < sql/example/mysql/create_database.sql
mysql -uroot -vvv -n < sql/example/mysql/create_table.sql
```
在两台压力机上执行,向数据库中加载数据
```bash
java -cp bin/:lib/mysql-connector-java-5.1.7-bin.jar iomark.TPCCRunner.Loader conf/example/mysql/loader.properties
```
在两台测试机上执行，在数据库中创建索引，加快查找速度
```bash
mysql -uroot -vvv -n < sql/example/mysql/create_index.sql
```
# 2.调优环境准备
压力机相当于客户端节点
## 2.1 运行环境准备
进入A-Tune仓库
```bash
cd /root/A-Tune/examples/tuning/mariadb_distributed
```
在压力机1上执行，运行prepare.sh脚本来替换调优文件中的路径，执行后还需输入压力机2的ip，和两台对应测试机的ip。
在压力机1上执行后，可以使用scp命令拷贝到另一台压力机
```bash
sh prepare.sh
```
本地执行命令的机器为client_ip_1，
压力机2的为client_ip_2，
两个mariadb数据库所在的测试机分别为server_ip_1、server_ip_2,
执行结果如下：
```bash
[root@localhost mariadb_distributed]# sh prepare.sh 
path: /root/gitee/A-Tune/examples/tuning/mariadb_distributed
[INPUT] enter client_ip_2 of testbench to used:9.82.199.187
[INPUT] enter server_ip_1 of testbench to used:9.82.179.1
[INPUT] enter server_ip_2 of testbench to used:9.82.199.161
[INFO] update path for mariadb files
[INFO] update ip for mariadb files
cp mariadb_server.yaml  to/etc/atuned/tuning
finish prepare
```

## 2.2 运行总的benchmark脚本
在压力机1上运行mariadb_benchmark.sh，该脚本同时进行本地和远程的benchmark运行，可以观察本地压力机debug_tpcc1.log日志、tpcc目录下的mariadb.log日志来查看运行过程：
```bash
sh mariadb_benchmark.sh
```

## 2.3 atune调优
atune-adm tuning 是 A-Tune 的调优命令，它会根据mariadb_client.yaml中的配置文件对mariadb数据库进行调优。会根据环境和性能数据自动选择合适的调优策略，优化集群的性能。调优过程中，可以通过查看mariadb.log、debug.log日志来确定服务是否正常执行：
```bash
atune-adm tuning --project mariadb --detail mariadb_client.yaml
```

执行调优命令后，会先执行benchmark获取基线数据，然后加载mariadb项目的调优配置文件，输出如下：
第一轮输出：
Best Performance: (tpmc=396916.00), Performance Improvement Rate: 3.95%
代表最优的性能指标，以及性能提升比例，对比基线是第一轮benchmark的结果。
```bash
[root@localhost mariadb_distributed]# atune-adm tuning --project mariadb --detail mariadb_client.yaml
 Start to benchmark baseline...
 1.Loading its corresponding tuning project: mariadb
 2.Start to tuning the system......
 Current Tuning Progress......(1/30)
 Used time: 10m27s, Total Time: 10m27s, Best Performance: (tpmc=396916.00), Performance Improvement Rate: 3.95%
 The 1th recommand parameters is: mariadb.key_buffer_size=1048576,mariadb.max_allowed_packet=20582912,mariadb.table_open_cache=66000,mariadb.back_log=3677,mariadb.sort_buffer_size=6963200,mariadb.read_buffer_size=16384000,mariadb.read_rnd_buffer_size=54272000,mariadb.thread_cache_size=462,mariadb.max_connections=1169,mariadb.max_heap_table_size=20480000,mariadb.innodb_log_buffer_size=63963136,mariadb.innodb_write_io_threads=5,mariadb.innodb_read_io_threads=10,innodb_buffer_pool_size=26843545000,innodb_buffer_pool_instances=3,innodb_io_capacity=1843
 The 1th evaluation value: (tpmc=396916.00)(3.95%)
```

## 2.4 恢复原有的配置参数（可选）
原始的参数配置文件为/var/atuned/ceph-tuning-restore.conf。
可以先执行如下命令恢复调优前的环境配置：
```bash
atune-adm tuning --restore --project mariadb
```
# 3.主要文件功能介绍
## set_mariadb_param_info.sh
该脚本在mariadb_server.yaml中使用，获取测试机1中mariadb相关的参数值,用来进行本地调优。（因为两台测试机硬件规格和环境比较相似，因此用使用第一个测试机的数据来进行调优即可）
如果需要扩展为不同机器的mariadb下发参数不同，可以扩展该脚本为两个参数，指定IP和参数名，用于给对应机器的参数进行下发。
```bash
#!/bin/bash
set -x

# 检查是否传入参数
if [ -z "$1" ]; then
  echo "请提供一个参数"
  exit 1
fi

# 获取传入的参数
param=$1


mysql -h SERVER_IP_1 -u root -e "SHOW VARIABLES LIKE '$1';" | grep -i "$1" | awk '{print $2}'
```
## set_mariadb_param_info.sh
该脚本用于下发参数到mariadb测试机节点，设置一对参数和值之后会将两个测试机节点设置相同的参数值，若需要多台机器设置不同的值此脚本需额外扩展一个参数IP用于指定对应机器进行参数下发
```bash
#!/bin/bash
set -x

# 检查是否传入参数
if [ -z "$1" ]; then
  echo "请提供一个参数"
  exit 1
fi

# 获取传入的参数
param=$1
value=$2

# 构建命令
ssh -q root@SERVER_IP_1 "bash -c 'grep -q \"^$param\" /etc/my.cnf && sed -i \"s/^$param.*/$param = $value/g\" /etc/my.cnf || echo \"$param = $value\" >> /etc/my.cnf'"

ssh -q root@SERVER_IP_2 "bash -c 'grep -q \"^$param\" /etc/my.cnf && sed -i \"s/^$param.*/$param = $value/g\" /etc/my.cnf || echo \"$param = $value\" >> /etc/my.cnf'"
```
## mariadb_benchmark.sh
该脚本是整体的benchmark执行脚本，用于在两台压力机执行性能压测并汇总结果到压力机1上。tpcc_benchmark.sh为本地执行benchmark脚本，remote_benchmark.sh为远程执行另一台压力机的脚本，该脚本会阻塞进程直到所有机器执行完benchmark结果并输出到mariadb_tpmc.out文件，最终通过get_tpmc.sh脚本将结果求和得到最终tpmc指标反馈给atune。

```bash
#!/bin/bash
set -x

cd PATH
sh tpcc_benchmark.sh >> debug_tpcc1.log 2>&1 &
local=$!
sh remote_benchmark.sh >> debug_tpcc2.log 2>&1 &
remote=$!

wait $local
wait $remote
```
## tpcc_benchmark.sh
该脚本用来执行本地benchmark，基于tpcc-runner基准测试程序进行压测。命令执行后会将结果重定向mariadb.log、slave1.log、slave2.log日志文件中，可以通过观察该日志文件来获取执行信息。
```bash
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
echo $total > mariadb_tpmc.out
```
## remote_benchmark.sh
该脚本用来在远程执行压力机2的benchmark，需要保证远程压力机的路径和当前环境的中的路径一致。
```bash
#!/bin/bash

# 在远程服务器上执行脚本并放入后台
ssh -q root@CLIENT_IP_2 "cd PATH && sh tpcc_benchmark.sh > tpcc_benchmark.log 2>&1 &"

sleep 5

# 监控远程日志，检测到特定日志内容时终止
while ! ssh -q root@CLIENT_IP_2 '[ -f PATH/tpcc/mariadb_tpmc.out ]'; do sleep 2; done && ssh -q root@CLIENT_IP_2 'kill $(pgrep -f tpcc_benchmark.sh)'

# # 等待所有后台进程完成
wait
```
