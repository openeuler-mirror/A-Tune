#!/bin/sh

path=$(
    cd "$(dirname "$0")"
    pwd
)
echo "path: ${path}"

read -p "[INPUT] enter client_ip_2 of testbench to used:" CLIENT_IP_2
read -p "[INPUT] enter server_ip_1 of testbench to used:" SERVER_IP_1
read -p "[INPUT] enter server_ip_2 of testbench to used:" SERVER_IP_2

echo "[INFO] update path for mariadb files"
sed -i "s#PATH#${path}#g" ${path}/get_mariadb_param_info.sh
sed -i "s#PATH#${path}#g" ${path}/get_tpmc.sh
sed -i "s#PATH#${path}#g" ${path}/mariadb_benchmark.sh
sed -i "s#PATH#${path}#g" ${path}/mariadb_client.yaml
sed -i "s#PATH#${path}#g" ${path}/mariadb_server.yaml
sed -i "s#PATH#${path}#g" ${path}/remote_benchmark.sh

echo "[INFO] update ip for mariadb files"
sed -i "s#SERVER_IP_1#$SERVER_IP_1#g" ${path}/get_mariadb_param_info.sh
sed -i "s#SERVER_IP_1#$SERVER_IP_1#g" ${path}/set_mariadb_param_info.sh
sed -i "s#SERVER_IP_2#$SERVER_IP_2#g" ${path}/set_mariadb_param_info.sh
sed -i "s#SERVER_IP_1#$SERVER_IP_1#g" ${path}/start_mariadb.sh
sed -i "s#SERVER_IP_2#$SERVER_IP_2#g" ${path}/start_mariadb.sh
sed -i "s#SERVER_IP_1#$SERVER_IP_1#g" ${path}/stop_mariadb.sh
sed -i "s#SERVER_IP_2#$SERVER_IP_2#g" ${path}/stop_mariadb.sh
sed -i "s#CLIENT_IP_2#$CLIENT_IP_2#g" ${path}/remote_benchmark.sh
sed -i "s#CLIENT_IP_2#$CLIENT_IP_2#g" ${path}/get_tpmc.sh

echo "cp mariadb_server.yaml  to/etc/atuned/tuning"
mkdir -p /etc/atuned/tuning
cp $path/mariadb_server.yaml /etc/atuned/tuning

echo "finish prepare"