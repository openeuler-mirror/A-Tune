#!/bin/sh

path=$1
disk=$2

cur=$(
  cd "$(dirname "$0")"
  pwd
)

echo "update the test script、client and server yaml files"
sed -i "s#^FILENAME.*#^FILENAME=${path}#g" $cur/iozone-test.sh
sed -i "s# .*iozone/iozone-test.sh# $cur/iozone-test.sh#g" $cur/tuning_iozone_server.yaml
sed -i "s# .*iozone/iozone-test.sh# $cur/iozone-test.sh#g" $cur/tuning_iozone_server.yaml
sed -i "s#DISKNAME#'${disk}#g" $cur/tuning_iozone_client.yaml

echo "copy the server yaml file to /etc/atuned/tuning/"
cp $cur/tuning_fio_server.yaml /etc/atuned/tuning/
