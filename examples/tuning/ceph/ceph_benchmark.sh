PG_NUMBER=200
PGP_NUMBER=200

echo "ceph benchmark start prep data."
if ceph osd pool ls |grep -q "^testbench$"; then
    echo "[WARN] pool testbench exist !!!"
else
    echo "[INFO] start create testbench ..."
    ceph osd pool create testbench ${PG_NUMBER} ${PGP_NUMBER}
    if [ $? -eq 0 ]; then
        echo "[INFO] Create testbench success ."
    else
        echo "[WARN] osd pool create testbench failed."
    fi
fi

rados -p testbench bench 10 write > ceph_iops_bandwidth_write.log     # write benchmark
# rados bench -p testbench 10 rand > ceph_iops_bandwidth_write.log    # random read benchmark, need write first
count=0
while true
do
    bandwidth_val=$(cat ceph_iops_bandwidth_write.log |grep "Bandwidth (MB/sec):" | awk -F ':' '{print $2}')
    iops_val=$(cat ceph_iops_bandwidth_write.log |grep "Average IOPS:" | awk -F ':' '{print $2}')
    if [ -z "${bandwidth_val}" ] || [ -z "${iops_val}" ]; then
        if [ ${count} -eq 10 ]; then
            echo "[ERROR] get val has reach 10 times, end !!!"
            break
        else
            count=$((${count}+1))
            sleep 3
        fi
        break
    else
        echo "${bandwidth_val} and ${iops_val}"
        break
    fi
done
echo 'bandwidth_val = '${bandwidth_val}
echo 'iops_val = '${iops_val}

