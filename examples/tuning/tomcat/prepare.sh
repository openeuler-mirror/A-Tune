#!/bin/sh
# Create: 2022-08-17

systemctl stop firewalld

echo "download tomcat"
rm -rf index.html
wget https://dlcdn.apache.org/tomcat/tomcat-10/
version=$(cat index.html | grep -oP '\d+\.\d+\.\d+' | tail -1)
wget https://dlcdn.apache.org/tomcat/tomcat-10/v$version/bin/apache-tomcat-$version.tar.gz
rm -rf index.html
echo "install tomcat"
tar -zxvf apache-tomcat-$version.tar.gz
echo "start tomcat"
./apache-tomcat-$version/bin/startup.sh

echo "install tomcat benchmark"
yum -y install httpd-tools

echo "set your tomcat folder"
root_tomcat=$1
sed -i 's#'root_tomcat'#'$root_tomcat'#' tuning_params_tomcat.yaml

echo "copy the tuning file to atune"
cp tuning_params_tomcat.yaml /etc/atuned/tuning/tomcat/
