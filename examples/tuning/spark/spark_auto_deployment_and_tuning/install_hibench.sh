#!/bin/bash
source ~/.bashrc

## Python 2.7
if ! command -v python2 &>/dev/null; then
    echo "downloading python-2.7..."
    wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
    if [ $? -eq 0 ]; then
        echo "------------ python-2.7 download success ------------" >./hibench.log
    else
        echo "------------ python-2.7 download failed  ------------" >>./hibench.log
        exit
    fi
    tar -xf ./Python-2.7.18.tgz
    rm -f ./Python-2.7.18.tgz
    # install python-2.7
    echo "installing python-2.7..."
    td=$(pwd)
    cd Python-2.7.18
    ./configure --prefix=$td/python-2.7
    make
    make install
    ln -s $td/python-2.7/bin/python2.7 /usr/bin/python2
    cd ..
fi

## Maven 3.8
echo "downloading maven..."
wget https://mirrors.tuna.tsinghua.edu.cn/apache/maven/maven-3/3.8.8/binaries/apache-maven-3.8.8-bin.tar.gz
if [ $? -eq 0 ]; then
    echo "------------ maven-3.8 download success ------------" >>./hibench.log
else
    echo "------------ maven-3.8 download failed  ------------" >>./hibench.log
    exit
fi
tar -xf ./apache-maven-3.8.8-bin.tar.gz
rm -f ./apache-maven-3.8.8-bin.tar.gz
export MAVEN_HOME=$(pwd)/apache-maven-3.8.8
if ! grep -q "export MAVEN_HOME=$(pwd)/apache-maven-3.8.8" ~/.bashrc; then
    echo "export MAVEN_HOME=$(pwd)/apache-maven-3.8.8" >>~/.bashrc
    echo "export PATH=\$PATH:\$MAVEN_HOME/bin" >>~/.bashrc
fi
source ~/.bashrc

# maven aliyun mirror
mkdir ~/.m2
cat >~/.m2/settings.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.2.0 https://maven.apache.org/xsd/settings-1.2.0.xsd">
    <mirrors>
        <mirror>
            <id>aliyunmaven</id>
            <mirrorOf>*</mirrorOf>
            <name>阿里云公共仓库</name>
            <url>https://maven.aliyun.com/repository/public</url>
        </mirror>
    </mirrors>
</settings>
EOF

# install HiBench
echo "installing HiBench..."
git clone https://github.com/Intel-bigdata/HiBench.git
if [ $? -eq 0 ]; then
    echo "------------ HiBench download success ------------" >>./hibench.log
else
    echo "------------ HiBench download failed  ------------" >>./hibench.log
    exit
fi
cd HiBench
if [ -n "$http_proxy" ]; then
    ip=$(echo $http_proxy | awk -F[/:] '{print $4}')
    port=$(echo $http_proxy | awk -F[/:] '{print $5}')
    mvn -Psparkbench -Dspark=3.1 -Dscala=2.12 -Dhttp.proxyHost=$ip -Dhttp.proxyPort=$port -Dhttps.proxyHost=$ip -Dhttps.proxyPort=$port clean package
else
    mvn -Psparkbench -Dspark=3.1 -Dscala=2.12 clean package
fi

if [ $? -eq 0 ]; then
    echo "------------ HiBench build success ------------" >>./hibench.log
else
    echo "------------ HiBench build failed  ------------" >>./hibench.log
    exit
fi
cp conf/hadoop.conf.template conf/hadoop.conf
sed -i "2c hibench.hadoop.home      $HADOOP_HOME" conf/hadoop.conf
sed -i "11c hibench.hdfs.master       hdfs://localhost:9000" conf/hadoop.conf

sed -i "s|hibench.scale.profile.*|hibench.scale.profile\thuge|g" conf/hibench.conf

cp conf/spark.conf.template conf/spark.conf
sed -i "2c hibench.spark.home      $SPARK_HOME" conf/spark.conf
sed -i "7c hibench.spark.master    spark://localhost:7077" conf/spark.conf
cd ..
echo "Hibench init success"