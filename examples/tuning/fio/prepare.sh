#!/bin/sh

disk=$2

cur=$(
  cd "$(dirname "$0")"
  pwd
)

echo "update the test script、client and server yaml files"
sed -i "s#^FILENAME.*#FILENAME=${disk}#g" $cur/fio-test.sh
sed -i "s# fio/fio-test.sh# $cur/fio-test.sh#g" $cur/tuning_fio_server.yaml
sed -i "s# fio/fio-test.sh# $cur/fio-test.sh#g" $cur/tuning_fio_client.yaml

echo "copy the server yaml file to /etc/atuned/tuning/"
cp $cur/tuning_fio_server.yaml /etc/atuned/tuning/
