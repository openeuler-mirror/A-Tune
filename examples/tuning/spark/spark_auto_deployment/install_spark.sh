#!/bin/bash

# install dependencies
echo "install dependencies..."
sudo dnf install gcc make curl wget samba git -y
if [ $? -eq 0 ]; then
    echo "------------ dependencies install success ------------" >>./install_spark.log
else
    echo "------------ dependencies install failed  ------------" >>./install_spark.log
    exit
fi

# stop firewalld
sudo systemctl disable --now firewalld

# start samba
sudo systemctl enable --now nmbd

### ssh password-free login
ssh-keygen -t rsa
cat ~/.ssh/id_rsa.pub >>~/.ssh/authorized_keys

# download and install software
# JDK 1.8
echo "downloading jdk..."
wget https://mirrors.tuna.tsinghua.edu.cn/Adoptium/8/jdk/x64/linux/OpenJDK8U-jdk_x64_linux_hotspot_8u372b07.tar.gz
if [ $? -eq 0 ]; then
    echo "------------ jdk-1.8 download success ------------" >>./install_spark.log
else
    echo "------------ jdk-1.8 download failed  ------------" >>./install_spark.log
    exit
fi
# install jdk
tar -xf ./OpenJDK8U-jdk_x64_linux_hotspot_8u372b07.tar.gz
export JAVA_HOME=$(pwd)/jdk8u372-b07
if ! grep -q "export JAVA_HOME=$(pwd)/jdk8u372-b07" ~/.bashrc; then
    echo "export JAVA_HOME=$(pwd)/jdk8u372-b07" >>~/.bashrc
    echo "export PATH=\$PATH:\$JAVA_HOME/bin" >>~/.bashrc
fi
source ~/.bashrc

## Hadoop
echo "downloading hadoop..."
wget https://mirrors.tuna.tsinghua.edu.cn/apache/hadoop/core/hadoop-3.2.4/hadoop-3.2.4.tar.gz
if [ $? -eq 0 ]; then
    echo "------------ hadoop-3.2 download success ------------" >>./install_spark.log
else
    echo "------------ hadoop-3.2 download failed  ------------" >>./install_spark.log
    exit
fi
# install hadoop
tar -xf ./hadoop-3.2.4.tar.gz
export HADOOP_HOME=$(pwd)/hadoop-3.2.4
if ! grep -q "export HADOOP_HOME=$(pwd)/hadoop-3.2.4" ~/.bashrc; then
    echo "export HADOOP_HOME=$(pwd)/hadoop-3.2.4" >>~/.bashrc
    echo "export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin" >>~/.bashrc
fi
cp ./conf/core-site.xml ./conf/hdfs-site.xml ./conf/mapred-site.xml ./conf/yarn-site.xml hadoop-3.2.4/etc/hadoop/
source ~/.bashrc

# start hadoop
$HADOOP_HOME/bin/hdfs namenode -format
if [ $? -eq 0 ]; then
    echo "------------ hadoop namenode format success ------------" >>./install_spark.log
else
    echo "------------ hadoop namenode format failed  ------------" >>./install_spark.log
    exit
fi
$HADOOP_HOME/sbin/start-dfs.sh
if [ $? -eq 0 ]; then
    echo "------------ hdfs startup success ------------" >>./install_spark.log
else
    echo "------------ hdfs startup failed  ------------" >>./install_spark.log
    exit
fi
$HADOOP_HOME/sbin/start-yarn.sh
if [ $? -eq 0 ]; then
    echo "------------ yarn startup success ------------" >>./install_spark.log
else
    echo "------------ yarn startup failed  ------------" >>./install_spark.log
    exit
fi

## Spark
echo "downloading spark"
wget https://archive.apache.org/dist/spark/spark-3.1.3/spark-3.1.3-bin-hadoop3.2.tgz
if [ $? -eq 0 ]; then
    echo "------------ spark-3.1 download success ------------" >>./install_spark.log
else
    echo "------------ spark-3.1 download failed  ------------" >>./install_spark.log
    exit
fi
# install spark
tar -xf ./spark-3.1.3-bin-hadoop3.2.tgz
export SPARK_HOME=$(pwd)/spark-3.1.3-bin-hadoop3.2
if ! grep -q "export SPARK_HOME=$(pwd)/spark-3.1.3-bin-hadoop3.2" ~/.bashrc; then
    echo "export SPARK_HOME=$(pwd)/spark-3.1.3-bin-hadoop3.2" >>~/.bashrc
    echo "export PATH=\$PATH:$\SPARK_HOME/bin:$\SPARK_HOME/sbin" >>~/.bashrc
fi

cp spark-3.1.3-bin-hadoop3.2/conf/spark-env.sh.template spark-3.1.3-bin-hadoop3.2/conf/spark-env.sh
echo "SPARK_MASTER_HOST=localhost" >>spark-3.1.3-bin-hadoop3.2/conf/spark-env.sh
cp spark-3.1.3-bin-hadoop3.2/conf/spark-defaults.conf.template spark-3.1.3-bin-hadoop3.2/conf/spark-defaults.conf
echo "spark.master                     spark://localhost:7077" >>spark-3.1.3-bin-hadoop3.2/conf/spark-defaults.conf
source ~/.bashrc

# start spark
$SPARK_HOME/sbin/start-master.sh
if [ $? -eq 0 ]; then
    echo "------------ spark master startup success ------------" >>./install_spark.log
else
    echo "------------ spark master startup failed  ------------" >>./install_spark.log
    exit
fi
$SPARK_HOME/sbin/start-worker.sh spark://localhost:7077
if [ $? -eq 0 ]; then
    echo "------------ spark worker startup success ------------" >>./install_spark.log
else
    echo "------------ spark worker startup failed  ------------" >>./install_spark.log
    exit
fi
echo "------------ spark example 'SparkPi' running  ------------" >>./install_spark.log
$SPARK_HOME/bin/run-example SparkPi
if [ $? -eq 0 ]; then
    echo "------------ 'SparkPi' execute success ------------" >>./install_spark.log
else
    echo "------------ 'SparkPi' execute failed  ------------" >>./install_spark.log
    exit
fi

echo "Spark deployment success."
