#!/bin/bash

echo "==========Check java environment=========="
java_result=`rpm -qa | grep "java"`
if [[ $java_result =~ "java" ]]
then
    echo "******The java environment has been configured******"
else
    sudo yum update -y
    sudo yum install java-1.8.0-openjdk* -y
    java_result=`rpm -qa | grep "java"`
    if [[ $java_result =~ "java" ]]
    then
        echo "******Success to configure the java environment******"
    else
        echo "******Failed to configure the java environment******"
    fi
fi

echo "==========Get java environment variables=========="
java_env=`which java`
java_env=`ls -lrt "$java_env"`
java_env=`echo "$java_env" | awk '{split($11, arr, " "); print arr[1]}'`
java_env=`ls -lrt "$java_env"`
java_env=`echo "$java_env" | awk '{split($11, arr, " "); print arr[1]}'`
str_array=(${java_env//\// })
java_env=""
for var in ${str_array[@]}
do
    if [[ "$var" == jre ]] ; then
        break
    else
        java_env=${java_env}"/"${var}
    fi
done

read -p "Do you want to configure JAVA_ HOME environment variable? ( yes | no ) :" choose
if [[ $choose == "yes" ]]
then
echo "==========Configure JAVA_ HOME environment variable=========="
file_name="/etc/profile.d/my_env.sh"
cat>$file_name<<EOF
export JAVA_HOME=$java_env
export JRE_HOME=\$JAVA_HOME/jre
export PATH=\$PATH:\$JAVA_HOME/bin
export CLASSPATH=.:\$JAVA_HOME/lib/dt.jar:\$JAVA_HOME/lib/tools.jar
EOF

echo "==========Make environment variables effective=========="
source /etc/profile
echo "******Success to configure the java environment******"
fi

echo "==========Get and configure node information=========="
read -p "Please enter the number of nodes: " node_num
read -p "Please enter the IP address of the master node: " node_arr[0]
for ((i=1;i<$node_num;i++))
do
    read -p "Please enter the IP of the ${i}th. slave node: " node_arr[$i]
done

echo "******Write node information to /etc/hosts******"
file_name="/etc/hosts"
for ((i=0;i<$node_num;i++))
do
((node_index=$i+1))
cat>>$file_name<<EOF
${node_arr[$i]} node$node_index
EOF
done

read -p "Do you want to configure hadoop environment(hadoop2.9.2)? ( yes | no ) :" choose
if [[ $choose == "yes" ]]
then
echo "==========Download hadoop=========="
mkdir /apps
cd /apps
wget http://archive.apache.org/dist/hadoop/core/hadoop-2.9.2/hadoop-2.9.2.tar.gz
tar -zxvf hadoop-2.9.2.tar.gz -C /apps
mv hadoop-2.9.2 hadoop
rm /apps/hadoop-2.9.2.tar.gz

echo "==========Configure hadoop environment=========="
hadoop_home="/apps/hadoop"
file_name="/etc/profile.d/my_env.sh"
cat>>$file_name<<EOF
export HADOOP_HOME=$hadoop_home
export CLASSPATH=\$(\$HADOOP_HOME/bin/hadoop classpath):\$CLASSPATH
export HADOOP_COMMON_LIB_NATIVE_DIR=\$HADOOP_HOME/lib/native
export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin
EOF

echo "==========Make environment variables effective=========="
source /etc/profile

echo "==========Modify hadoop configuration files=========="
echo "******Modify core-site.xml******"
mkdir /apps/data
mkdir /apps/data/hadoop
file_name="/apps/hadoop/etc/hadoop/core-site.xml"
cat>$file_name<<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <!-- Set the default file system. Hadoop supports file systems such as file、HDFS、GFS、ali|Amazon cloud, etc -->
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://node1:8020</value>
    </property>

    <!-- Set Hadoop local save data path -->
    <property>
        <name>hadoop.tmp.dir</name>
        <value>/apps/data/hadoop</value>
    </property>

    <!-- Set HDFS web UI user identity -->
    <property>
        <name>hadoop.http.staticuser.user</name>
        <value>root</value>
    </property>

    <!-- Integrate hive user agent settings -->
    <property>
        <name>hadoop.proxyuser.root.hosts</name>
        <value>*</value>
    </property>

    <property>
        <name>hadoop.proxyuser.root.groups</name>
        <value>*</value>
    </property>

    <!-- File system trash can retention time -->
    <property>
        <name>fs.trash.interval</name>
        <value>1440</value>
    </property>
</configuration>
EOF

echo "******Modify hdfs-site.xml******"
file_name="/apps/hadoop/etc/hadoop/hdfs-site.xml"
cat>$file_name<<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <!-- Set SNN process running machine location information -->
    <property>
        <name>dfs.namenode.secondary.http-address</name>
        <value>node2:9868</value>
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

echo "******Modify yarn-site.xml******"
file_name="/apps/hadoop/etc/hadoop/yarn-site.xml"
cat>$file_name<<EOF
<?xml version="1.0"?>
<configuration>
    <!-- Site specific YARN configuration properties -->
    <!-- Set the running machine position of the main color of the YARN cluster -->
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>node1</value>
    </property>

    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>

    <!-- Whether physical memory limits will be enforced on the container -->
    <property>
        <name>yarn.nodemanager.pmem-check-enabled</name>
        <value>false</value>
    </property>

    <!-- Whether virtual memory limits will be enforced on containers -->
    <property>
        <name>yarn.nodemanager.vmem-check-enabled</name>
        <value>false</value>
    </property>

    <!-- Turn on log aggregation -->
    <property>
        <name>yarn.log-aggregation-enable</name>
        <value>true</value>
    </property>

    <!-- Set the address of the yarn history server -->
    <property>
        <name>yarn.log.server.url</name>
        <value>http://node1:19888/jobhistory/logs</value>
    </property>

    <!-- The history log is saved for 7 days -->
    <property>
        <name>yarn.log-aggregation.retain-seconds</name>
        <value>604800</value>
    </property>
</configuration>
EOF

echo "******Modify mapred-site.xml******"
file_name="/apps/hadoop/etc/hadoop/mapred-site.xml"
cat>$file_name<<EOF
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <!-- Set the default running mode of the MR program: yarn cluster mode local mode -->
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>

    <!-- MR program history service address -->
    <property>
        <name>mapreduce.jobhistory.address</name>
        <value>node1:10020</value>
    </property>
    
    <!-- Web address of MR program history server -->
    <property>
        <name>mapreduce.jobhistory.webapp.address</name>
        <value>node1:19888</value>
    </property>

    <property>
        <name>yarn.app.mapreduce.am.env</name>
        <value>HADOOP_MAPRED_HOME=\${HADOOP_HOME}</value>
    </property>

    <property>
        <name>mapreduce.map.env</name>
        <value>HADOOP_MAPRED_HOME=\${HADOOP_HOME}</value>
    </property>

    <property>
        <name>mapreduce.reduce.env</name>
        <value>HADOOP_MAPRED_HOME=\${HADOOP_HOME}</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>/apps/hadoop/share/hadoop/mapreduce/*, /apps/hadoop/share/hadoop/mapreduce/lib/*</value>
    </property>
</configuration>
EOF

echo "******Modify hadoop-env.sh******"
file_name="/apps/hadoop/etc/hadoop/hadoop-env.sh"
cat>>$file_name<<EOF
export JAVA_HOME=$java_env
export HDFS_NAMENODE_USER=root
export HDFS_DATANODE_USER=root
export HDFS_SECONDARYNAMENODE_USER=root
export YARN_RESOURCEMANAGER_USER=root
export YARN_NODEMANAGER_USER=root
EOF

echo "******Modify yarn-env.sh******"
file_name="/apps/hadoop/etc/hadoop/yarn-env.sh"
cat>>$file_name<<EOF
export JAVA_HOME=$java_env
EOF

echo "******Modify mapred-env.sh******"
file_name="/apps/hadoop/etc/hadoop/mapred-env.sh"
cat>>$file_name<<EOF
export JAVA_HOME=$java_env
EOF

echo "******Modify slaves******"
file_name="/apps/hadoop/etc/hadoop/slaves"
cat>$file_name<<EOF
EOF
for ((i=1;i<=$node_num;i++))
do
cat>>$file_name<<EOF
node$i
EOF
done
fi

read -p "Do you want to configure ssh password less login? ( yes | no ) :" choose
if [[ $choose == "yes" ]]
then
echo "==========SSH login without password=========="
ssh localhost "cd ~/.ssh"
rm ~/.ssh/id_rsa*
ssh-keygen -t rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
for ((i=2;i<=$node_num;i++))
do
    scp /etc/hosts root@node$i:/etc/hosts
done
for ((i=2;i<=$node_num;i++))
do  
    ssh node$i "cd ~/.ssh;rm ~/.ssh/id_rsa*;ssh-keygen -t rsa"
    scp root@node$i:~/.ssh/id_rsa.pub ~/authorized_keys_node$i
    cat ~/authorized_keys_node$i >> ~/.ssh/authorized_keys
    rm ~/authorized_keys_node$i
done
for ((i=2;i<=$node_num;i++))
do  
    scp ~/.ssh/authorized_keys root@node$i:~/.ssh
done
fi

echo "==========Turn off the firewall=========="
yum install ntpdate -y
for ((i=2;i<=$node_num;i++))
do  
    ssh node$i "yum install ntpdate -y"
done
systemctl stop firewalld.service
systemctl disable firewalld.service
for ((i=2;i<=$node_num;i++))
do  
    ssh node$i "systemctl stop firewalld.service"
    ssh node$i "systemctl disable firewalld.service"
done

echo "==========Synchronize cluster time=========="
ntpdate ntp5.aliyun.com
for ((i=2;i<=$node_num;i++))
do  
    ssh node$i "ntpdate ntp5.aliyun.com"
done

echo "==========Cluster distribution script xsync=========="
yum install rsync -y
for ((i=2;i<=$node_num;i++))
do  
    ssh node$i "yum install rsync -y"
done
cd /usr/bin
file_name="/usr/bin/xsync"
cat>$file_name<<EOF
#!/bin/bash
# Judge the number of the parameters
if [ \$# -lt 1 ]
then
    echo Not Enough Argument!
    exit;
fi
# Traverse all machines in the cluster
read -p "Please enter the number of nodes: " ip_num
for ((i=1;i<=\$ip_num;i++))
do
    echo ===================== node\$i =========================
    # Traverse all directories and send them one by one
    for file in \$@
    do
        # Judge whether the file exists
        if [ -e \$file ]
            then
                # Get Parent Directory
                pdir=\$(cd -P \$(dirname \$file); pwd)

                # Get the current file name
                fname=\$(basename \$file)
                ssh node\$i "mkdir -p \$pdir"
                rsync -av \$pdir/\$fname node\$i:\$pdir
            else
                echo \$file does not exists!
        fi
    done
done
EOF

echo "******Give permissions to xsync******"
chmod +x /usr/bin/xsync

echo "******Distribute xsync to other nodes******"
cd /usr
xsync ./bin

echo "==========Modify /etc/hostname=========="
file_name="/etc/hostname"
for ((i=2;i<=$node_num;i++))
do
cat>$file_name<<EOF
node$i
EOF
scp /etc/hostname root@node$i:/etc/
done
cat>$file_name<<EOF
node1
EOF

read -p "Do you want to configure the java environment for the slave node? ( yes | no ) :" choose
if [[ $choose == "yes" ]]
then
echo "==========Configure the java environment for the slave node=========="
for ((i=2;i<=$node_num;i++))
do  
    ssh node$i "sudo yum update -y"
    ssh node$i "sudo yum install java-1.8.0-openjdk* -y"
done
cd /etc/profile.d
xsync ./my_env.sh
for ((i=2;i<=$node_num;i++))
do  
    ssh node$i "source /etc/profile.d/my_env.sh"
done
fi

read -p "Do you want to distribute hadoop files to slave nodes? ( yes | no ) :" choose
if [[ $choose == "yes" ]]
then
cd /apps
xsync ./hadoop
cd /etc/profile.d
xsync ./my_env.sh
for ((i=2;i<=$node_num;i++))
do  
    ssh node$i "source /etc/profile.d/my_env.sh"
done
fi

echo "==========Activate the environment in the slave node=========="
for ((i=2;i<=$node_num;i++))
do  
    ssh node$i "source /etc/profile"
done

echo "==========Initialize hadoop=========="
/apps/hadoop/bin/hdfs namenode -format
sh start-all.sh

echo "==========Create a folder for storing program running history on HDFS=========="
hadoop fs -mkdir /sparklog
hadoop fs -chmod 777 /sparklog

read -p "Do you want to install anaconda3(anaconda3-5.2.0)? ( yes | no ) :" choose
if [[ $choose == "yes" ]]
then
echo "==========Install anaconda3=========="
cd /apps
mkdir ./anaconda_install
cd ./anaconda_install
wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/Anaconda3-5.2.0-Linux-x86_64.sh
sh ./Anaconda3-5.2.0-Linux-x86_64.sh
source ~/.bashrc
source activate
rm -rf /apps/anaconda_install
echo "******Create a new python 2.7 environment named Spark******"
conda create -n spark python=2.7
source activate spark
mkdir /root/.pip
touch /root/.pip/pip.conf
chmod 666 /root/.pip/pip.conf
file_name="/root/.pip/pip.conf"
cat>$file_name<<EOF
[global]
index-url = https://pypi.mirrors.ustc.edu.cn/simple/
[install]
trusted-host = https://pypi.mirrors.ustc.edu.cn/
EOF
pip install pyhive pyspark jieba -i https://pypi.tuna.tsinghua.edu.cn/simple
for ((i=2;i<=$node_num;i++))
do 
    ssh node$i "mkdir /root/.pip"
    scp /root/.pip/pip.conf root@node$i:/root/.pip/
    ssh node$i "cd /apps;mkdir ./anaconda_install;cd ./anaconda_install;wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/Anaconda3-5.2.0-Linux-x86_64.sh;sh ./Anaconda3-5.2.0-Linux-x86_64.sh;source ~/.bashrc;source activate;rm -rf /apps/anaconda_install"
    ssh node$i "conda create -n spark python=2.7;source activate spark;pip install pyhive pyspark jieba -i https://pypi.tuna.tsinghua.edu.cn/simple"
done
fi

read -p "Do you want to install Spark(spark2.4.0)? ( yes | no ) :" choose
if [[ $choose == "yes" ]]
then
echo "==========Install spark2.4.0=========="
cd /apps
wget https://archive.apache.org/dist/spark/spark-2.4.0/spark-2.4.0-bin-hadoop2.7.tgz
tar -zxvf /apps/spark-2.4.0-bin-hadoop2.7.tgz -C /apps
mv /apps/spark-2.4.0-bin-hadoop2.7 /apps/spark
rm /apps/spark-2.4.0-bin-hadoop2.7.tgz
fi

read -p "Do you want to configure the spark environment? ( yes | no ) :" choose
if [[ $choose == "yes" ]]
then
echo "==========Configure Spark environment=========="
file_name="/etc/profile"
cat>>$file_name<<EOF
export JAVA_HOME=$java_env
export JRE_HOME=\$JAVA_HOME/jre
export PATH=\$PATH:\$JAVA_HOME/bin
export CLASSPATH=.:\$JAVA_HOME/lib/dt.jar:\$JAVA_HOME/lib/tools.jar
export HADOOP_HOME=/apps/hadoop
export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin
export HADOOP_CONF_DIR=\$HADOOP_HOME/etc/hadoop
export YARN_CONF_DIR=\$HADOOP_HOME/etc/hadoop
export SPARK_HOME=/apps/spark
export PATH=\$PATH:\$SPARK_HOME/bin:\$SPARK_HOME/sbin
export PYSPARK_PYTHON=/apps/anaconda3/envs/spark/bin/python
EOF
file_name="/root/.bashrc"
cat>>$file_name<<EOF
export JAVA_HOME=$java_env
export PYSPARK_PYTHON=/apps/anaconda3/envs/spark/bin/python
EOF
source /etc/profile
source /root/.bashrc

echo "==========Modify the Spark configuration files=========="
echo "******Modify slaves******"
mv /apps/spark/conf/slaves.template /apps/spark/conf/slaves
file_name="/apps/spark/conf/slaves"
cat>$file_name<<EOF
EOF
for ((i=1;i<=$node_num;i++))
do
cat>>$file_name<<EOF
node$i
EOF
done

echo "******Modify spark-env.sh******"
mv /apps/spark/conf/spark-env.sh.template /apps/spark/conf/spark-env.sh
file_name="/apps/spark/conf/spark-env.sh"
cat>>$file_name<<EOF
## Set the JAVA installation directory
JAVA_HOME=$java_env

## HADOOP software configuration file directory, read files on HDFS and run YARN cluster
HADOOP_CONF_DIR=/apps/hadoop/etc/hadoop
YARN_CONF_DIR=/apps/hadoop/etc/hadoop

## Specify the IP address of the Spark Master and the communication port for submitting tasks
# Inform which machine the Spark master is running on
# export SPARK_MASTER_HOST=node1
# Inform the communication port of the Spark master
export SPARK_MASTER_PORT=7077
# Inform the webui port of the spark master
SPARK_MASTER_WEBUI_PORT=8080

# Number of available cores of worker cpu
SPARK_WORKER_CORES=1
# worker available memory
SPARK_WORKER_MEMORY=1g
# Work address of worker
SPARK_WORKER_PORT=7078
# The webui address of the worker
SPARK_WORKER_WEBUI_PORT=8081

## Set History Server
# The configuration means to save the running history log of the Spark program in the /sparklog folder of hdfs
SPARK_HISTORY_OPTS="-Dspark.history.fs.logDirectory=hdfs://node1:8020/sparklog/ -Dspark.history.fs.cleaner.enabled=true"
EOF

echo "******Modify spark-defaults.conf******"
mv /apps/spark/conf/spark-defaults.conf.template /apps/spark/conf/spark-defaults.conf
file_name="/apps/spark/conf/spark-defaults.conf"
cat>>$file_name<<EOF
# Enable the date recording function of Spark
spark.eventLog.enabled true
# Set the path of spark logging
spark.eventLog.dir hdfs://node1:8020/sparklog/ 
# Set whether to start compression of Spark logs
spark.eventLog.compress false
EOF

echo "******Modify log4j.properties******"
mv /apps/spark/conf/log4j.properties.template /apps/spark/conf/log4j.properties
file_name="/apps/spark/conf/log4j.properties"
cat>$file_name<<EOF
# Set everything to be logged to the console
log4j.rootCategory=WARN, console
log4j.appender.console=org.apache.log4j.ConsoleAppender
log4j.appender.console.target=System.err
log4j.appender.console.layout=org.apache.log4j.PatternLayout
log4j.appender.console.layout.ConversionPattern=%d{yy/MM/dd HH:mm:ss} %p %c{1}: %m%n

# Set the default spark-shell/spark-sql log level to WARN. When running the
# spark-shell/spark-sql, the log level for these classes is used to overwrite
# the root logger's log level, so that the user can have different defaults
# for the shell and regular Spark apps.
log4j.logger.org.apache.spark.repl.Main=WARN
log4j.logger.org.apache.spark.sql.hive.thriftserver.SparkSQLCLIDriver=WARN

# Settings to quiet third party logs that are too verbose
log4j.logger.org.sparkproject.jetty=WARN
log4j.logger.org.sparkproject.jetty.util.component.AbstractLifeCycle=ERROR
log4j.logger.org.apache.spark.repl.SparkIMain\$exprTyper=INFO
log4j.logger.org.apache.spark.repl.SparkILoop\$SparkILoopInterpreter=INFO
log4j.logger.org.apache.parquet=ERROR
log4j.logger.parquet=ERROR

# SPARK-9183: Settings to avoid annoying messages when looking up nonexistent UDFs in SparkSQL with Hive support
log4j.logger.org.apache.hadoop.hive.metastore.RetryingHMSHandler=FATAL
log4j.logger.org.apache.hadoop.hive.ql.exec.FunctionRegistry=ERROR

# For deploying Spark ThriftServer
# SPARK-34128:Suppress undesirable TTransportException warnings involved in THRIFT-4805
log4j.appender.console.filter.1=org.apache.log4j.varia.StringMatchFilter
log4j.appender.console.filter.1.StringToMatch=Thrift error occurred during processing of message
log4j.appender.console.filter.1.AcceptOnMatch=false
EOF
fi

read -p "Do you want to distribute spark to slave nodes(spark2.4.0)? ( yes | no ) :" choose
if [[ $choose == "yes" ]]
then
echo "==========Distribute spark to slave nodes=========="
cd /etc
xsync ./profile
cd /root
xsync ./.bashrc
cd /apps
xsync ./spark
for ((i=2;i<=$node_num;i++))
do
    ssh node$i "source /etc/profile"
    ssh node$i "source /root/.bashrc"
done
fi

read -p "Do you want to configure scala environment(scala2.11.0)? ( yes | no ) :" choose
if [[ $choose == "yes" ]]
then
echo "==========Configure scala environment=========="
cd /apps
wget https://downloads.lightbend.com/scala/2.11.0/scala-2.11.0.tgz
tar -zxvf /apps/scala-2.11.0.tgz -C /apps
mv /apps/scala-2.11.0 /apps/scala
rm /apps/scala-2.11.0.tgz
file_name="/etc/profile"
cat>>$file_name<<EOF
export SCALA_HOME=/apps/scala
export PATH=\$PATH:\$SCALA_HOME/bin
EOF
source /etc/profile
for ((i=2;i<=$node_num;i++))
do
    scp -r /apps/scala root@node$i:/apps/
    scp /etc/profile root@node$i:/etc
    ssh node$i "source /etc/profile"
done
fi

read -p "Do you want to configure maven environment(maven3.5.4)? ( yes | no ) :" choose
if [[ $choose == "yes" ]]
then
cd /apps
wget https://archive.apache.org/dist/maven/maven-3/3.5.4/binaries/apache-maven-3.5.4-bin.tar.gz
tar -zxvf /apps/apache-maven-3.5.4-bin.tar.gz -C /apps
sed -i'.bak' -ne '\#'"<mirrors>"'#{p;:a;n;\#'"</mirrors>"'#!ba;i\'"    <mirror\>\n      <id\>alimaven</id\>\n      <mirrorOf\>central</mirrorOf\>\n      <name\>aliyun maven</name\>\n      <url\>http://maven.aliyun.com/nexus/content/groups/public/</url\>\n    </mirror\>" -e '};p' /apps/apache-maven-3.5.4/conf/settings.xml
rm /apps/apache-maven-3.5.4-bin.tar.gz
file_name="/etc/profile"
cat>>$file_name<<EOF
export MAVEN_HOME=/apps/apache-maven-3.5.4
export PATH=\${MAVEN_HOME}/bin:\${PATH}
EOF
source /etc/profile
fi

read -p "Do you want to configure the hibench environment? ( yes | no ) :" choose
if [[ $choose == "yes" ]]
then
echo "==========Configure HiBench environment=========="
yum install bc
yum install git -y
cd /apps
git clone https://github.com/Intel-bigdata/HiBench.git
cd /apps/HiBench
mvn -Phadoopbench -Psparkbench -Dspark=2.4 -Dscala=2.11 clean package
cp /apps/HiBench/conf/hadoop.conf.template /apps/HiBench/conf/hadoop.conf
sed -i 's/\/PATH\/TO\/YOUR\/HADOOP\/ROOT/\/apps\/hadoop/g' /apps/HiBench/conf/hadoop.conf
sed -i 's/hdfs:\/\/localhost:8020/hdfs:\/\/node1:8020/g' /apps/HiBench/conf/hadoop.conf
cp /apps/HiBench/conf/spark.conf.template /apps/HiBench/conf/spark.conf
sed -i 's/\/PATH\/TO\/YOUR\/SPARK\/HOME/\/apps\/spark/g' /apps/HiBench/conf/spark.conf
fi

stop-all.sh
start-all.sh

source activate spark
for ((i=2;i<=$node_num;i++))
do 
    ssh node$i "source activate spark"
done

echo "==========Select the spark program to tune=========="
read -p "Please select the spark program to tune ( sort  terasort  wordcount  kmeans  svm  nweight  pagerank ): " program
cp -r /A-Tune/examples/tuning/spark/spark_hibench_template /A-Tune/examples/tuning/spark/spark_hibench_$program
mv /A-Tune/examples/tuning/spark/spark_hibench_$program/spark_hibench_template_client.yaml /A-Tune/examples/tuning/spark/spark_hibench_$program/spark_hibench_${program}_client.yaml
mv /A-Tune/examples/tuning/spark/spark_hibench_$program/spark_hibench_template_server.yaml /A-Tune/examples/tuning/spark/spark_hibench_$program/spark_hibench_${program}_server.yaml
mv /A-Tune/examples/tuning/spark/spark_hibench_$program/spark_hibench_template.sh /A-Tune/examples/tuning/spark/spark_hibench_$program/spark_hibench_${program}.sh
sed -i 's/{program}/'"${program}"'/g' /A-Tune/examples/tuning/spark/spark_hibench_$program/prepare.sh
sed -i 's/{program}/'"${program}"'/g' /A-Tune/examples/tuning/spark/spark_hibench_$program/README
sed -i 's/{program}/'"${program}"'/g' /A-Tune/examples/tuning/spark/spark_hibench_$program/spark_hibench_${program}_client.yaml
sed -i 's/{program}/'"${program}"'/g' /A-Tune/examples/tuning/spark/spark_hibench_$program/spark_hibench_${program}_server.yaml
sed -i 's/{program}/'"${program}"'/g' /A-Tune/examples/tuning/spark/spark_hibench_$program/spark_hibench_${program}.sh
cd /A-Tune/examples/tuning/spark/spark_hibench_$program
sh ./prepare.sh