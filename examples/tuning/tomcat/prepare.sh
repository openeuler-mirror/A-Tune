#!/bin/sh
# Create: 2022-08-17

systemctl stop firewalld

echo "download tomcat"
wget https://dlcdn.apache.org/tomcat/tomcat-10/v10.0.23/bin/apache-tomcat-10.0.23.tar.gz
echo "install tomcat"
tar -zxvf apache-tomcat-10.0.23.tar.gz
echo "start tomcat"
./apache-tomcat-10.0.23/bin/startup.sh

echo "install tomcat benchmark"
yum -y install httpd-tools

echo "set your tomcat folder"
root_tomcat=$1
sed -i 's/'root_tomcat'/'$root_tomcat'/' tuning_params_tomcat.yaml

echo "copy the tuning file to atune"
cp tuning_params_tomcat.yaml /etc/atuned/tuning/tomcat/
