path=$(
  cd "$(dirname "$0")"
  pwd
)

echo "update the client and server yaml files"
sed -i "s#sh .*spark/spark_hibench_{program}/spark_hibench_{program}.sh#sh $path/spark_hibench_{program}.sh#g" "$path"/spark_hibench_{program}_client.yaml
sed -i "s# spark/spark_hibench_{program}/spark_hibench_{program}.sh# $path/spark_hibench_{program}.sh#g" "$path"/spark_hibench_{program}_server.yaml

echo "copy the server yaml file to /etc/atuned/tuning/"
cp $path/spark_hibench_{program}_server.yaml /etc/atuned/tuning/

echo "create test data"
read -p "Please select the data scale ( tiny  small  large  huge  gigantic  bigdata ): " data_size
sed -i "3c hibench.scale.profile    ${data_size}" /apps/HiBench/conf/hibench.conf

sh /apps/HiBench/bin/workloads/ml/{program}/prepare/prepare.sh