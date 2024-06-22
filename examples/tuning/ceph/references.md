declare -A ceph1_info=(
    ["ip"]="ip1"
    ["port"]=22
    ["username"]="root"
    ["password"]="Huawei12#$"
    ["hostname"]="CLIENT1"
)

declare -A ceph1_info=(
    ["ip"]="ip2"
    ["port"]=22
    ["username"]="root"
    ["password"]="Huawei12#$"
    ["hostname"]="CEPH1"
)

declare -A ceph2_info=(
    ["ip"]="ip3"
    ["port"]=22
    ["username"]="root"
    ["password"]="Huawei12#$"
    ["hostname"]="CEPH2"
)

declare -A ceph3_info=(
    ["ip"]="ip4"
    ["port"]=22
    ["username"]="root"
    ["password"]="Huawei12#$"
    ["hostname"]="CEPH3"
)

function remote_sshpass() {
    echo "[remote_sshpass] $1"
    declare -n ref_dict=$1
    # echo "pw: ${ref_dict['password']}"
    command_str=$2
    # local escaped_cmd_str=$(echo "$command_str" | sed 's/"/\\"/g') # escaped_command_str=$(printf '%q ' "$command_str") 
    echo "[CMD] command_str: ${command_str}"
    password=${ref_dict['password']}
    port=${ref_dict['port']}
    username=${ref_dict['username']}
    host_ip=${ref_dict['ip']}
    local com="sshpass -p '${ref_dict['password']}' ssh -p ${ref_dict['port']} ${ref_dict['username']}@${ref_dict['ip']} 'bash -s' <<< \"${command_str}\""
    echo "[INFO] [CMD] $com"
    eval $com
}


function remote_sshpass_shell() {
    echo "[remote_sshpass] $1"
    declare -n ref_dict=$1
    echo "pw: ${ref_dict['password']}"
    script=$2
    if [ ! -f ${script} ];then
        echo "[FATAL] ${script} do not exist"
        exit
    fi
    echo "[CMD] command_str: ${command_str}"
    password=${ref_dict['password']}
    port=${ref_dict['port']}
    username=${ref_dict['username']}
    host_ip=${ref_dict['ip']}
    local com="sshpass -p '${ref_dict['password']}' ssh -p ${ref_dict['port']} ${ref_dict['username']}@${ref_dict['ip']} < '${script}'"
    echo "[CMD] $com"
    eval $com
}

# main ceph
cmd="systemctl stop firewalld;
systemctl disable firewalld;
setenforce 0;
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config;
"

echo "[CEPH1] ${cmd}"
eval ${cmd}
declare -a dict_names=("ceph2_info" "ceph3_info")
for dict_name in ${dict_names[@]}; do
    echo "[INFO] current dict_name: ${dict_name}"
    remote_sshpass ${dict_name} "${cmd}"
done


cmd="
unset http_proxy;
unset https_proxy;
yum -y install ntpdate;
yum -y install expect;
yum -y install sshpass;
crontab -l;
/usr/sbin/ntpdate 172.19.1.63 >> /var/log/szntp01.log 2>&1;
"
echo "[CEPH1] ${cmd}"
eval ${cmd}
declare -a dict_names=("ceph2_info" "ceph3_info")
for dict_name in ${dict_names[@]}; do
    echo "[INFO] current dict_name: ${dict_name}"
    remote_sshpass ${dict_name} "${cmd}"
done
eval ${cmd}

tmpdir=`pwd`'/tmp.sh'
chmod a+x ${tmpdir}
echo "sed -i '/CEPH/d' /etc/hosts" > ${tmpdir}
for dict_name in ${dict_names[@]}; do
    echo "[INFO] host current dict_name: ${dict_name}"
    declare -n ref_dict=$dict_name
    echo "echo \"${ref_dict['ip']} ${ref_dict['hostname']}\" >> /etc/hosts" >> ${tmpdir}
done
./tmp.sh
exit

echo "[INFO] host info\n: ${hosts_content}"
echo -e "$hosts_content" >> /etc/hosts

for dict_name in ${dict_names[@]}; do
    echo "[INFO] current dict_name: ${dict_name}"
    remote_sshpass ${dict_name} "echo -e '${hosts_content}' >> /etc/hosts"
done

rsa_dir="~/.ssh/id_rsa"
rsa_dir_gen="/root/.ssh/id_rsa.pub"
echo 'if ! id cephadmin &>/dev/null; then
    useradd cephadmin
    echo "Huawei12#$"| passwd --stdin cephadmin
    echo "cephadmin ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/cephadmin
    chmod 0440 /etc/sudoers.d/cephadmin
else
    echo "User cephadmin already exists."
fi' > ${tmpdir}
chmod a+x tmp.sh
./tmp.sh
declare -a dict_names=("ceph2_info" "ceph3_info")
for dict_name in ${dict_names[@]}; do
    echo "[INFO] current dict_name: ${dict_name}"
    remote_sshpass_shell ${dict_name} "tmp.sh"
done
# --------------------------------------------------------------------------
echo "
su -cephadmin -c \"
if [ -f ${rsa_dir} ];then
    rm ${rsa_dir}
fi
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N \\\"\\\"
" > ${tmpdir}

for dict_name in ${dict_names[@]}; do
    declare -n ref_dict=${dict_name}
    echo "sshpass -p ${ref_dict['password']} ssh-copy-id -i ${rsa_dir_gen} -p ${ref_dict['port']} cephadmin@${ref_dict['ip']}" >> ${tmpdir}
done
echo "\"" >> ${tmpdir}
./tmp.sh
echo "Finished load in local tmp.sh cephadmin."

# --------------------------------------------------------------------------
echo "[INFO] exec here ceph1_info"
main_match_name="ceph1_info"
for dict_name in ${dict_names[@]};do
    echo "[INFO] ----------------------------    current info is: ${dict_name}    -----------------------"
    echo "su -cephadmin -c \"                                      
if [ -f ${rsa_dir} ];then
    rm ${rsa_dir}
fi
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N \\\"\\\"
    " > ${tmpdir}
    new_dict=()
    for dict_n in ${dict_names[@]};
    do
        if [ "${dict_n}" != "${dict_name}" ];then
            echo "[DEBUG] dict_n vs dict_name, ${dict_n} vs ${dict_name}"
            declare -n ref_dict=${dict_n}
            echo "sshpass -p ${ref_dict['password']} ssh-copy-id -i ${rsa_dir_gen} -p ${ref_dict['port']} cephadmin@${ref_dict['ip']}" >> ${tmpdir}
        fi
    done
    declare -n ref_dict=${main_match_name}
    echo "sshpass -p ${ref_dict['password']} ssh-copy-id -i ${rsa_dir_gen} -p ${ref_dict['port']} cephadmin@${ref_dict['ip']}" >> ${tmpdir}
    echo "\"" >> ${tmpdir}
    cat "[INFO] cmd: \n :"` cat ${tmpdir}`
    echo "[INFO] current dict_name: ${dict_name}, tmp.sh: `cat ${tmpdir}`"
    echo "[INFO]"
    remote_sshpass_shell ${dict_name} "tmp.sh"
done

# remote_sshpass "ceph2_info" "./tmp.sh"

____________________________________________________________________________________________________________________________________
***ceph 安装建议直接 yum install ceph 安装***
git clone https://gitee.com/src-openeuler/ceph.git
cd ceph
git checkout openEuler-22.03-LTS-SP1
yum install CUnit-devel boost-random cryptsetup-devel expat-devel fmt-devel fuse-devel gperf gperftools-devel leveldb-devel libaio-devel libbabeltrace-devel libblkid-devel libcap-ng-devel libibverbs-devel libicu-devel libnl3-devel liboath-devel librabbitmq-devel lttng-ust-devel lua-devel luarocks lz4-devel nasm nss-devel openldap-devel xmlstarlet xfsprogs-devel valgrind-devel sqlite-devel snappy-devel selinux-policy-devel python3-sphinx python3-devel python3-Cython openldap-devel nss-devel nasm lz4-devel luarocks lua-devel lttng-ust-devel /usr/bin/pathfix.py  libudev-devel libtool libxml2-devel python3-prettytable
mkdir -p ~/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS} 
cp *.patch /root/rpmbuild/SOURCES/ 
cp ceph-*.tar.gz /root/rpmbuild/SOURCES/
cp ceph.spec /root/rpmbuild/SPECS/ 
cp ceph.yaml /root/rpmbuild/SOURCES/
rpmbuild -ba ceph.spec
cp /root/rpmbuild/SRPMS/ceph-*.src.rpm ./
rpm -ivh ceph-*.src.rpm
____________________________________________________________________________________________________________________________________
pip3 install git+https://github.com/ceph/ceph-deploy.git
mkdir ceph-cluster
cd ceph-cluster/

ceph-cluster]$ cat ceph.conf
......
public network = 192.168.122.0/24
cluster network = 192.168.122.0/24
____________________________________________________________________________________________________________________________________
# 在任意一台机器上即可， 可以是 client*， 或者 ceph*， 配置对于 host 文件
ceph-deploy new ceph1 ceph2 ceph3
"""
/etc/ceph.conf 文件加上
public_network = 192.168.122.0/24
cluster_network = 192.168.122.0/24
[mon]
mon_allow_pool_delete = true
"""
-------------------
ceph-deploy mon create-initial

# 执行成功后生成的“ceph.client.admin.keyring”拷贝到各个节点上
ceph-deploy --overwrite-conf admin ceph1 ceph2 ceph3 client1

# 部署MGR节点
ceph-deploy mgr create ceph1 ceph2 ceph3

# 通过 client 链接 ceph{1-3}
ceph-deploy admin client1 ceph1 ceph2 ceph3

ceph config set mon auth_allow_insecure_global_id_reclaim false
___________________________________________________________________________________
192.168.122.24 client1   gala-oe2203sp1-yyg-0928       
192.168.122.14 ceph1     gala-test-env-v2r9            50G
192.168.122.23 ceph2     gala-test-env-cdc-oe2203sp1   50G
192.168.122.12 ceph3     aops-controller-2203-lts-sp1  50G

# 创建 osd 存储
ceph-deploy disk zap ceph1 /dev/sda3
ceph-deploy osd create ceph1 --data /dev/sda3
ceph-deploy disk zap ceph2 /dev/sda3
ceph-deploy osd create ceph2 --data /dev/sda3
ceph-deploy disk zap ceph3 /dev/sda3
ceph-deploy osd create ceph3 --data /dev/sda3
___________________________________________________________________________________
# ceph 性能测试， 参考 https://www.ibm.com/docs/zh/storage-ceph/7.1?topic=administration-ceph-performance-benchmark
在运行这些性能测试之前，请通过运行以下命令来删除所有文件系统高速缓存
准备: echo 3 | sudo tee /proc/sys/vm/drop_caches && sudo sync
1) 创建新的存储池:        ceph osd pool create testbench 200 200
   如果想要删除测试对象:   rados -p testbench cleanup
   如果想要删除存储池:	    ceph osd pool delete testbench testbench --yes-i-really-really-mean-it
2) 对新创建的存储池运行写测试 10 秒
   rados bench -p testbench 10 write --no-cleanup
   重要指标解释(操作数， 读写请求次数)
		Total time run:         10.8337                 总运行时间 10.8s
		Average IOPS:           16		                平均每秒输入/输出操作数（IOPS），单位是每秒操作数（ops/s）
		Bandwidth (MB/sec):     66.4595                 带宽，单位是每秒兆字节（MB/s）  66.4MB
		Average Latency(s):     0.935594                平均延迟时间， 单位 s
3) 对存储池运行顺序读测试 10 秒
   rados bench -p testbench 10 seq
   Total time run:        0.804869
   Bandwidth (MB/sec):    139.153

   Average Latency:       0.420841
   Max latency:           0.706133
   Min latency:           0.0816332
   
4) 对存储池运行随机读测试 10 秒（随机读写 10 秒更加适合作为标准指标）
   rados bench -p testbench 10 rand
   Total time run:       10.036
	Total reads made:     4042
	Read size:            4194304
	Object size:          4194304
	Bandwidth (MB/sec):   1610.99
	Average IOPS:         402
	Stddev IOPS:          176.91
	Max IOPS:             509
	Min IOPS:             0
	Average Latency(s):   0.0389749
	Max latency(s):       3.11751
	Min latency(s):       0.00295484
5) 参数可修改
   -t 选项，线程数，缺省值为 16 个线程
   -b 参数可以调整正在写入的对象的大小。 缺省对象大小为 4 MB。 安全最大对象大小为 16 MB
   --run-name 执行写入的对象名称， 防止多客户同时访问同一对应导致 IO 错误
   rados bench -p testbench 10 write -t 4 -b 8388608 --run-name client1

6) 除去 rados bench 命令创建的数据(非删除整个存储池):
   rados -p testbench cleanup
   
___________________________________________________________________________________
ceph.conf 可以调整的参数，调优相关的
osd_pool_default_size = 3       默认值 3， 3副本能足够保证数据的可靠性；
osd_pool_default_min_size = 1   默认值 0

在内部使用的ceph集群中一般配置为none，即不使用认证，这样能适当加快ceph集群访问速度；
auth_service_required = none    默认值 "cephx"
auth_client_required = none     默认值 "cephx, none"
auth_cluster_required = none    默认值 "cephx"

osd client端objecter的throttle配置，它的配置会影响librbd，RGW端的性能
objecter_inflight_ops = 10240               默认值 1024
objecter_inflight_op_bytes = 1048576000     默认值 100M

这个是osd端收到client messages的capacity配置，配置大的话能提升osd的处理能力，但会占用较多的系统内存；服务器内存足够大的时候，适当增大这两个值
osd_client_message_size_cap = 1048576000    默认值 500*1024L*1024L     // client data allowed in-memory (in bytes)
osd_client_message_cap = 10000              默认值 100     // num client messages allowed in-memory
___________________________________________________________________________________
ceph参数：filestore
filestore xattr use omap                为xattrs使用object map，ext4 文件系统时时有，xfs或者btrfs                   {false, true}
filestore max sync interval             日志到数据盘最大同步间隔                                                    {}
filestore min sync interval             日志到数据盘最小同步间隔                                                    {}
filestore queue max ops                 数据盘最大接受操作数                                                        {}
filestore queue max bytes               数据盘一次操作最大字节数                                                    {}
filestore queue committing max ops      数据盘能过commit的操作数                                                   {}
filestore queue committing max bytes    数据盘能过commit的最大字节数                                                {}
filestore op threads                    并发文件系统操作数                                                         {}
___________________________________________________________________________________
ceph参数：OSD优化
osd max write size                      OSD 一次可写入的最大值（MB)                                                 {}
osd client message size cap             客户端允许在内存中的最大数据（bytes)
osd deep scrub stride                   在deep scrub时允许读取字节数(bytes)
osd op threads                          OSD进程操作的线程数
osd disk threads                        OSD 密集型操作例如恢复和scrubbing时的线程
osd map cache size                      保留OSD map的缓存（MB)
osd map cache bi size                   OSD 进程在内存中的OSD Map 缓存（MB)
___________________________________________________________________________________
PG number 调整
PG_number = OSD 15个，副本数：3. PG数目= 15*100/3 = 500 ~= 512
cephx_sign_messages=false #默认开启，对安全要求不高时建议关闭
filestore_fd_cache_size=4096 #默认256
filestore_fd_cache_shards=256 #默认16
___________________________________________________________________________________
系统层面
预读：read_aheah_kb建议更大值
进程：pid_max设更大值
调整CPU频率，使其运行在更高性能下。
SWAP: vm.swappiness=0
___________________________________________________________________________________
主要性能指标: IOPS和MBPS(吞吐率)
echo "8192" > /sys/block/sda/queue/read_ahead_kb                   设置磁盘的预读缓存
echo 4194303 > /proc/sys/kernel/pid_max                            设置系统的进程数量
执行生效：                                         sysctl -p /etc/sysctl.d/ceph.conf
___________________________________________________________________________________


# 网址参考
[ceph 介绍](https://www.cnblogs.com/liugp/p/17018394.html)
[ceph 安装参考1](https://cloud-atlas.readthedocs.io/zh-cn/latest/ceph/deploy/install_ceph.html)
[ceph 安装参考2](https://www.cnblogs.com/weir110/p/16127590.html)
[ceph 性能手动调优参考1](https://bbs.huaweicloud.com/blogs/346804)
[ceph 性能手动调优参考2](https://www.cnblogs.com/lemanlai/p/13646160.html)
[ceph 格式化 osd 磁盘失效解决方案](https://www.cnblogs.com/zbhlinux/p/16987425.html)
[ceph 性能评测](https://www.ibm.com/docs/zh/storage-ceph/6?topic=benchmark-benchmarking-ceph-performance)
[ceph 卸载, 当频繁失败初始化 osd 之后可以卸载重装](https://www.cnblogs.com/nulige/articles/8475907.html)








																

																
																
																
																
																
																

    











