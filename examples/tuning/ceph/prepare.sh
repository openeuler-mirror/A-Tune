#!/bin/sh

path=$(
    cd "$(dirname "$0")"
    pwd
)
echo "path: ${path}"

read -p "[INPUT] enter PG_NUMBER of testbench to used:" PG_NUMBER
read -p "[INPUT] enter PGP_NUMBER of testbench to used:" PGP_NUMBER

echo "[INFO] update the client and server yaml files"
sed -i "s#PATH#${path}#g" ${path}/ceph_client.yaml
sed -i "s#PG_NUMBER=.*#PG_NUMBER=$PG_NUMBER#g" ${path}/ceph_benchmark.sh
sed -i "s#PATH#${path}#g" ${path}/ceph_server.yaml

if [ ! -d /etc/atuned/tuning/ceph ]; then
    mkdir /etc/atuned/tuning/ceph
fi
cp ${path}/ceph_server.yaml /etc/atuned/tuning/ceph/ceph_server.yaml

