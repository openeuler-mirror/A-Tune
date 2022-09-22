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

echo "set FILE_PATH to the path of enwik8 in compress_Except_example.py"
sed -i "s#compress_Except_example/enwik8#$path/enwik8#g" "$path"/compress_Except_example.py

echo "update the client and server yaml files"
sed -i "s#python3 .*compress_Except_example.py#python3 $path/compress_Except_example.py#g" "$path"/compress_Except_example_client.yaml
sed -i "s# compress_Except_example/compress_Except_example.py# $path/compress_Except_example.py#g" "$path"/compress_Except_example_server.yaml

echo "copy the server yaml file to /etc/atuned/tuning/"
cp "$path"/compress_Except_example_server.yaml /etc/atuned/tuning/
