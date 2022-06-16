#!/bin/sh

cur=$(
  cd "$(dirname "$0")"
  pwd
)

echo "update the test script、client and server yaml files"

sed -i "s#cd stream/#cd $cur/#g" $cur/tuning_stream_client.yaml
sed -i "s#.stream/Makefile# $cur/Makefile#g" $cur/tuning_stream_server.yaml


echo "copy the server yaml file to /etc/atuned/tuning/"
cp tuning_stream_server.yaml /etc/atuned/tuning/


wget http://www.cs.virginia.edu/stream/FTP/Code/stream.c
