#!/bin/bash

# download and install software
# JDK 1.8
echo "downloading jdk..."
wget https://mirrors.ustc.edu.cn/adoptium/releases/temurin8-binaries/jdk8u372-b07/OpenJDK8U-jdk_x64_linux_hotspot_8u372b07.tar.gz
if [ $? -eq 0 ]; then
    echo "------------ jdk-1.8 download success ------------" >>./install_spark.log
else
    echo "------------ jdk-1.8 download failed  ------------" >>./install_spark.log
    exit
fi
# install jdk
tar -xf ./OpenJDK8U-jdk_x64_linux_hotspot_8u372b07.tar.gz
rm -f ./OpenJDK8U-jdk_x64_linux_hotspot_8u372b07.tar.gz
export JAVA_HOME=$(pwd)/jdk8u372-b07
if ! grep -q "export JAVA_HOME=$(pwd)/jdk8u372-b07" ~/.bashrc; then
    echo "export JAVA_HOME=$(pwd)/jdk8u372-b07" >>~/.bashrc
    echo "export PATH=\$PATH:\$JAVA_HOME/bin" >>~/.bashrc
fi
source ~/.bashrc

## Hadoop
echo "downloading hadoop..."
wget https://mirrors.ustc.edu.cn/apache/hadoop/core/hadoop-3.2.4/hadoop-3.2.4.tar.gz
if [ $? -eq 0 ]; then
    echo "------------ hadoop-3.2 download success ------------" >>./install_spark.log
else
    echo "------------ hadoop-3.2 download failed  ------------" >>./install_spark.log
    exit
fi
# install hadoop
tar -xf ./hadoop-3.2.4.tar.gz
rm -f ./hadoop-3.2.4.tar.gz
export HADOOP_HOME=$(pwd)/hadoop-3.2.4
if ! grep -q "export HADOOP_HOME=$(pwd)/hadoop-3.2.4" ~/.bashrc; then
    echo "export HADOOP_HOME=$(pwd)/hadoop-3.2.4" >>~/.bashrc
    echo "export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin" >>~/.bashrc
fi
cat >hadoop-3.2.4/etc/hadoop/core-site.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
    <property>
        <name>hadoop.tmp.dir</name>
        <value>$(pwd)/tmp</value>
    </property>
</configuration>
EOF

cat >hadoop-3.2.4/etc/hadoop/hdfs-site.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.safemode.threshold.pct</name>
        <value>0</value>
        <description>
            Specifies the percentage of blocks that should satisfy
            the minimal replication requirement defined by dfs.replication.min.
            Values less than or equal to 0 mean not to wait for any particular
            percentage of blocks before exiting safemode.
            Values greater than 1 will make safe mode permanent.
        </description>
    </property>
</configuration>
EOF

cat >hadoop-3.2.4/etc/hadoop/mapred-site.xml <<EOF
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>\$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/*:\$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/*</value>
    </property>
</configuration>
EOF

cat >hadoop-3.2.4/etc/hadoop/yarn-site.xml <<EOF
<?xml version="1.0"?>
<configuration>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <property>
    <name>yarn.nodemanager.env-whitelist</name>
    <value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_HOME,PATH,LANG,TZ,HADOOP_MAPRED_HOME</value>
  </property>
    <property>
        <name>yarn.nodemanager.pmem-check-enabled</name>
        <value>false</value>
    </property>
    <property>
        <name>yarn.nodemanager.vmem-check-enabled</name>
        <value>false</value>
    </property>
</configuration>

EOF

cat >>hadoop-3.2.4/etc/hadoop/hadoop-env.sh <<EOF
export JAVA_HOME=$JAVA_HOME
export HDFS_NAMENODE_USER=root
export HDFS_DATANODE_USER=root
export HDFS_SECONDARYNAMENODE_USER=root
export YARN_RESOURCEMANAGER_USER=root
export YARN_NODEMANAGER_USER=root
EOF

cat >>hadoop-3.2.4/etc/hadoop/yarn-env.sh <<EOF
export JAVA_HOME=$JAVA_HOME
EOF
cat >>hadoop-3.2.4/etc/hadoop/mapred-env.sh <<EOF
export JAVA_HOME=$JAVA_HOME
EOF
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
rm -f ./spark-3.1.3-bin-hadoop3.2.tgz
export SPARK_HOME=$(pwd)/spark-3.1.3-bin-hadoop3.2
if ! grep -q "export SPARK_HOME=$(pwd)/spark-3.1.3-bin-hadoop3.2" ~/.bashrc; then
    echo "export SPARK_HOME=$(pwd)/spark-3.1.3-bin-hadoop3.2" >>~/.bashrc
    echo "export PATH=\$PATH:\$SPARK_HOME/bin:\$SPARK_HOME/sbin" >>~/.bashrc
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
