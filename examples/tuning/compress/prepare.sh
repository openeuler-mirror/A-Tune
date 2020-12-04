#!/usr/bin/bash
if [ "$#" -ne 1 ]; then
  echo "USAGE: $0 the path of enwik8.zip"
  exit 1
fi

path=$(
  cd "$(dirname "$0")"
  pwd
)

echo "unzip enwik8.zip"
unzip "$path"/enwik8.zip

echo "set FILE_PATH to the path of enwik8 in compress.py"
sed -i "s#compress/enwik8#$path/enwik8#g" "$path"/compress.py

echo "update the client and server yaml files"
sed -i "s#python3 .*compress.py#python3 $path/compress.py#g" "$path"/compress_client.yaml
sed -i "s# compress/compress.py# $path/compress.py#g" "$path"/compress_server.yaml

echo "copy the server yaml file to /etc/atuned/tuning/"
cp "$path"/compress_server.yaml /etc/atuned/tuning/
