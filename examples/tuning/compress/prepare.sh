#!/usr/bin/bash
if [ "$#" -ne 1 ] ; then      
	echo "USAGE: $0 the path of enwik8.zip"
	exit -1
fi

work_path=$(dirname $(readlink -f $0))
echo "current working path is $work_path"

file_path=`echo $work_path|sed 's/\//\\\\\//g'`

echo "unzip enwik8.zip"
unzip $1 -d $work_path/

echo "set file_path to the path of enwik8 in compress.py"
sed -i "s/^file_path\ = \s*[0-9,a-z,A-Z,\",\/,\-]*/file_path\ = \"$file_path\/enwik8\"/g" $work_path/compress.py

echo "update the client and server yaml files"
sed -i "s/^benchmark\ : \"python3\ \s*[0-9,a-z,A-Z,\",\/,\-]*compress.py\"/benchmark\ : \"python3 $file_path\/compress.py\"/g" $work_path/compress_client.yaml
sed -i "s/\/\s*[0-9,a-z,A-Z,\",\/,\-]*compress.py/$file_path\/compress.py/g" $work_path/compress_server.yaml

echo "copy the server yaml file to /etc/atuned/tuning/"
cp $work_path/compress_server.yaml /etc/atuned/tuning/
