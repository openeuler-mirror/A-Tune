# 1.环境准备

## 1.1部署ceph集群

准备四台网络互通的虚拟机环境：​
client：​客户端节点，管理和监控 Ceph 集群。​
ceph1、ceph2、ceph3：​Ceph 集群的存储节点。

### 1.1.1 设置主机名
分别在四个节点上执行重命名命令，设置相应的主机名，用于区分不同功能的节点：
```bash
hostnamectl set-hostname client     #client节点执行
hostnamectl set-hostname ceph1      #ceph1节点执行
hostnamectl set-hostname ceph2      #ceph2节点执行
hostnamectl set-hostname ceph3      #ceph3节点执行
```
设置新的主机名后，使用 hostnamectl 来查看是否配置生效，通常看到 Static hostname: client 这行内容表示设置成功。
### 1.1.2 配置主机映射
在四个节点上配置hosts文件（路径 /etc/hosts），使服务器之间可以通过主机名互相访问，（根据实际 IP 地址进行修改）：
```bash
vim /etc/hosts      #打开hosts文件，添加节点的 IP 地址和主机名映射

9.82.154.180 client
9.82.222.129 ceph1
9.82.247.43 ceph2
9.82.179.1 ceph3
```
hosts文件配置后，确认各个节点之间可以互相ping通。如：
```bash
ping ceph1
```
### 1.1.3 配置SSH免密登录

ceph安装过程中需要多次输入机器的密码，可以通过配置免密登录提升效率。

本地生成密钥，执行此命令后按Enter键可以全部采用默认的配置。
```bash
ssh-keygen
```
将公钥分发到各个节点，分发公钥过程中需要输入相应虚拟机的密码：
```bash
ssh-copy-id root@ceph1
ssh-copy-id root@ceph2
ssh-copy-id root@ceph3
```
验证免密登录，远程虚拟机免密登录后，可以使用 exit 命令返回本地虚拟机：
```bash
ssh root@ceph1
ssh root@ceph2
ssh root@ceph3
```
### 1.1.4 关闭防火墙（可选）

为避免防火墙阻止 Ceph 节点之间的通信，在所有节点上暂时关闭防火墙：

```bash
systemctl stop firewalld
systemctl disable firewalld
```

### 1.1.5 安装ceph

所有节点（client、ceph1、ceph2、ceph3）上分别安装 Ceph 软件包。执行以下命令：
```bash
yum install ceph -y
```
### 1.1.5 下载ceph-deploy自动化部署工具
在 client 节点上，使用 pip3 安装 ceph-deploy 工具，该工具用于简化 Ceph 集群的部署和管理，通过 SSH 在远程主机上执行命令，自动化 Ceph 集群的部署过程：
```bash
pip3 install git+https://github.com/ceph/ceph-deploy.git
```
安装过程中会有warning告警，可以忽略，使用--help命令来查看是否安装成功。ceph-deploy --help会列出所有的可用命令和选项：
```bash
ceph-deploy --help
```
### 1.1.6 初始化ceph集群


**创建配置文件目录**

在client节点上执行，创建一个用于存放集群配置和密钥的目录：
```bash
mkdir ceph-cluster
cd ceph-cluster/
```
**创建ceph节点**

在 client 节点上，使用 ceph-deploy 创建一个新的 Ceph 集群配置，指定初始的监视器（MON）节点。执行后将在当前目录生成一个 ceph.conf 配置文件，包含指定的 MON 节点信息：
```bash
ceph-deploy new ceph1 ceph2 ceph3
```
各节点之间如果没有配置免密，命令执行后需要多次输入密码。
该命令执行成功后会生成文件ceph.conf（Ceph 集群的配置文件），ceph.mon.keyring（Monitor 节点的密钥文件），ceph-deploy-ceph.log（Monitor 节点的日志文件）。
**部署MON服务**

在 client 节点上，部署并初始化 MON 服务：
```bash
ceph-deploy mon create-initial
```
执行成功后会在管理节点上生成密钥文件，如ceph.client.admin.keyring等，包含ceph集群的认证密钥。

**将 ceph.client.admin.keyring 拷贝到各个节点上**

在client节点上执行，为了确保各个节点能与集群进行交互，将认证密钥文件（ceph.client.admin.keyring）分发到所有的 Ceph 节点和客户端节点：
```bash
ceph-deploy --overwrite-conf admin ceph1 ceph2 ceph3 client
```
该命令成功执行后，会将当前目录下的ceph.conf，ceph.client.admin.keyring文件推送到指定的节点（ceph1、ceph2、ceph3 和 client）的/etc/ceph/ 目录下，并覆盖目标节点的同名文件。
**部署MGR节点**

在client节点上执行，为ceph1、ceph2、ceph3三个节点部署 MGR 服务，保证集群的监控和管理功能正常运行：
```bash
ceph-deploy mgr create ceph1 ceph2 ceph3
```
**配置客户端访问**

在client节点执行，客户端可以通过 Ceph 的配置文件来访问集群：
```bash
ceph-deploy admin client ceph1 ceph2 ceph3
```
执行成功后，可以通过 ceph -s 来查看集群中的守护管理进程（ceph-mgr）是否正常运行。
**禁用不安全的MON认证恢复**

在client节点执行，auth_allow_insecure_global_id_reclaim 是 Ceph 配置中的一个参数，默认情况下，Ceph 可能会在认证恢复时使用全局 ID，禁用它可以提高集群的安全性：
```bash
ceph config set mon auth_allow_insecure_global_id_reclaim false
```
执行过程中没有error报错，表示执行成功。
**创建OSD存储**

在三个ceph节点，ceph1、ceph2、ceph3上执行。
查看磁盘使用情况，列出系统中的所有磁盘和分区，选择一个空闲的磁盘来作为 OSD 存储，下面命令以/dev/sda3为例：
```bash
lsblk
```
三个ceph节点分别执行如下命令，注意disk zap 操作会擦除磁盘上的所有数据，建议提前数据备份。osd create 操作会将该磁盘创建为 Ceph 集群中的 OSD 存储设备：
```bash
ceph-deploy disk zap ceph1 /dev/sda3
ceph-deploy osd create ceph1 --data /dev/sda3
ceph-deploy disk zap ceph2 /dev/sda3
ceph-deploy osd create ceph2 --data /dev/sda3
ceph-deploy disk zap ceph3 /dev/sda3
ceph-deploy osd create ceph3 --data /dev/sda3
```
可以查看ceph的日志文件来查看详细命令执行过程，确保执行成功：
```bash
tail -f /var/log/ceph/ceph.log
```
### 1.1.7 确认集群搭建完成

执行以下命令来查看ceph-mon服务的状态，确保所有ceph节点都正常运行。如果所有节点都显示为 active (running)，则说明ceph节点已成功启动：
```bash
systemctl status ceph-mon@ceph1
systemctl status ceph-mon@ceph2
systemctl status ceph-mon@ceph3
```

查看集群的健康状态、OSD 节点、MON 节点的运行状态等信息：
```bash
ceph -s
```
正常输出结果，
有3个监视器守护进程（ceph1、ceph2、ceph3），它们已组成法定人数（quorum）并且运行正常，有3个管理守护进程（mgr.ceph1 是活动的，ceph2 和 ceph3 是备用的），有存储池和存储的对象。
```bash
[root@client ceph]# ceph -s
  cluster:
    id:     27a84062-b91f-447d-a9a7-e184df2d9ed5
    health: HEALTH_WARN
            clock skew detected on mon.ceph2
            1 pool(s) do not have an application enabled
 
  services:
    mon: 3 daemons, quorum ceph1,ceph2,ceph3 (age 105m)
    mgr: ceph1(active, since 28h), standbys: ceph2, ceph3
    osd: 3 osds: 3 up (since 28h), 3 in (since 28h)
 
  data:
    pools:   2 pools, 33 pgs
    objects: 2 objects, 577 KiB
    usage:   414 MiB used, 2.6 GiB / 3.0 GiB avail
    pgs:     33 active+clean

```
## 1.2安装Atune

具体安装启动方式参考A-Tune README-zh 文档第一节“安装A-Tune”,A-Tune仓库链接：https://gitee.com/openeuler/A-Tune

```bash
yum install -y atune atune-engine
```
加载并启动atuned和atune-engine服务:
```bash
systemctl start atuned
systemctl start atune-engine
```
# 2.对ceph进行调优
## 2.1 克隆仓库
克隆 A-Tune 调优脚本仓库：
```bash
cd ~
git clone https://gitee.com/openeuler/A-Tune.git
cd A-Tune/examples/tuning/ceph
```
## 2.2 调优准备
为调优过程提供所需的环境,执行命令后需要手动输入测试参数 PG（Placement Group）和 PGP（Placement Group Primary）。
Placement Groups (PG) 是 Ceph 中用于将对象分组管理的基本单位。Ceph 将存储池中的对象分配到不同的 PG 中，然后根据 CRUSH 算法将这些 PG 分配给 OSDs（对象存储设备）。
PGP (Placement Group for Placement) 指的是 PG 在进行数据放置时所使用的数量。当创建或修改存储池时，设置的 pgp_num 决定了 Ceph 如何计算数据放置的位置。
```bash
sh prepare.sh
#执行后手动输入参数200：
#[INPUT] enter PG_NUMBER of testbench to used:200
#[INPUT] enter PGP_NUMBER of testbench to used:200
```
执行命令后可以查看/etc/atuned/tuning/ceph目录下是否存在ceph_server.yaml文件，如果文件存在证明执行成功。
```bash
ll /etc/atuned/tuning/ceph/ceph_server.yaml
```

## 2.3 获取基线数据（可选）
使用以下命令运行基准测试脚本 ceph_benchmark.sh，获取集群的初始性能数据（基线数据）：
```bash
sh ceph_benchmark.sh
```
执行该命令主要是用来验证benchmark脚本正常，执行成功后会有如下结果,会输出一个带宽值和iops值：
```bash
[root@client ceph]# sh ceph_benchmark.sh 
ceph benchmark start prep data.
[WARN] pool testbench exist !!!
     23.8809 and            5
bandwidth_val =  23.8809
iops_val =  5
```
该脚本ceph_benchmark.sh用来对ceph集群进行性能基准测试，主要是通过rados命令对 Ceph 集群中的 OSD (对象存储守护进程) 执行 IO 性能测试，并收集带宽和IOPS (每秒输入/输出操作数) 相关的数据。
可以通过查看当前路径下ceph_iops_bandwidth_write.log文件来观察具体的性能基线数据测试过程：
```bash
tail -f ceph_iops_bandwidth_write.log
```
## 2.4 atune调优
atune-adm tuning 是 A-Tune 的调优命令，它会根据ceph_client.yaml中的配置文件对 Ceph 集群进行调优。会根据环境和性能数据自动选择合适的调优策略，优化集群的性能。调优过程中，可以通过查看ceph_iops_bandwidth_write.log来确定服务是否正常执行benchmark：
```bash
atune-adm tuning --project ceph --detail ceph_client.yaml
```
执行调优命令后，会先执行benchmark获取基线数据，然后加载ceph项目的调优配置文件，输出如下：
第一轮输出：
Best Performance: (bandwidth=24.51,iops_val=6.00), Performance Improvement Rate: 16.63%
代表最优的性能指标，以及性能提升比例，对比基线是第一轮benchmark的结果。
```bash
[root@client ceph]# atune-adm tuning --project ceph --detail ceph_client.yaml
 Start to benchmark baseline...
 1.Loading its corresponding tuning project: ceph
 2.Start to tuning the system......
 Current Tuning Progress......(1/30)
 Used time: 45s, Total Time: 45s, Best Performance: (bandwidth=24.51,iops_val=6.00), Performance Improvement Rate: 16.63%
 The 1th recommand parameters is: ceph.rbd_op_threads=8,vm.swappiness=20,pid_max=5243076,filestore_max_sync_interval=3,osd_map_cache_size=400,filestore_min_sync_interval=0.071,filestore_op_threads=14,osd_max_write_size=810,ceph.osd_pool_default_size=9,osd_deep_scrub_stride=972864,filestore_queue_max_bytes=104857600,osd_client_message_size_cap=1206632960
 The 1th evaluation value: (bandwidth=24.51,iops_val=6.00)(16.63%)
```
最后一轮输出：

```bash
Current Tuning Progress......(30/30)
 Used time: 8m46s, Total Time: 8m46s, Best Performance: (bandwidth=26.18,iops_val=6.00), Performance Improvement Rate: 20.49%
 The 30th recommand parameters is: ceph.rbd_op_threads=1,vm.swappiness=0,pid_max=4615316,filestore_max_sync_interval=3,osd_map_cache_size=400,filestore_min_sync_interval=0.071,filestore_op_threads=14,osd_max_write_size=230,ceph.osd_pool_default_size=9,osd_deep_scrub_stride=972864,filestore_queue_max_bytes=209715200,osd_client_message_size_cap=766231040
 The 30th evaluation value: (bandwidth=26.18,iops_val=6.00)(20.49%)
 
 The final optimization result is: ceph.rbd_op_threads=1,vm.swappiness=0,pid_max=4615316,filestore_max_sync_interval=3,osd_map_cache_size=400,filestore_min_sync_interval=0.071,filestore_op_threads=14,osd_max_write_size=230,ceph.osd_pool_default_size=9,osd_deep_scrub_stride=972864,filestore_queue_max_bytes=209715200,osd_client_message_size_cap=766231040
 The final evaluation value is: bandwidth=26.18,iops_val=6.00

 Baseline Performance is: (bandwidth=21.64,iops_val=5.00)
 
 Tuning Finished
```
每进行一次迭代，就会给出较好的的参数值，并将参数值打印到屏幕上，如osd_map_cache_size=400,filestore_min_sync_interval=0.071等。
调优执行完最后一个迭代轮次后，会把性能提升最大的一组参数配置值设置到当前环境中并生效。如果想恢复最初的基线数据，可参考2.5.
## 2.5 恢复原有的配置参数（可选）
原始的参数配置文件为/var/atuned/ceph-tuning-restore.conf。
可以先执行如下命令恢复调优前的环境配置：
```bash
atune-adm tuning --restore --project mariadb
```

# 3.项目结构介绍

```shell
examples/tuning/ceph
├── ceph_benchmark.sh					ceph性能benchmark脚本
├── ceph_client.yaml					atune客户端配置文件，指导atune如何运行benchmark脚本以及如何获取当前关注的性能指标		
├── ceph_server.yaml					atune服务端配置文件，指导atune如何关闭和开启应用，以及各个参数如何获取参数值、如何设置参数值生效,ceph_server.yaml文件是进行atune调优的主要yaml文件，包含ceph集群的调优参数。
├── get_ceph_param_info.sh				获取ceph参数值的脚本
├── prepare_install.sh					自动化安装ceph的脚本，可能随着ceph更新导致脚本失效，建议手动部署ceph集群
├── prepare.sh							调优前准备脚本，主要用于配置压测相关参数、脚本路径以及拷贝配置文件到指定目录，供atune服务端使用
├── README.md							指导文档		
└── references.md						参考文档
```
## ceph_benchmark.sh
该脚本在A-Tune调优过程中获取ceph集群的性能基线数据，创建testbench资源池提供一个用于基准测试的存储区域，并设定池的 PG (Placement Groups) 为 200，PGP (Placement Group for placement) 为200。
使用rados命令对testbench池进行写入基准测试，-p 表示对名为testbench的存储池进行性能测试，bench表示性能测试模式，10表示测试持续时间为10s，write表示测试写入操作。测试结果（IOPS 和带宽）会被输出到ceph_iops_bandwidth_write.log日志文件中。之后输出基准测试结果，打印带宽（MB/sec）和平均IOPS值。


ceph_benchmark.sh源代码如下：
```bash
PG_NUMBER=200
PGP_NUMBER=200

echo "ceph benchmark start prep data."

#创建ceph集群的pool池，命名为testbench
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

#使用rados命令对ceph集群的testbench池进行反复读写，生成带宽和IOPS值。命令执行结果重定向到ceph_iops_bandwidth_write.log日志文件中，在atune调优过程中也可以观察该过程
rados -p testbench bench 10 write > ceph_iops_bandwidth_write.log     # write benchmark

count=0
while true
do
    #通过查看ceph_iops_bandwidth_write.log文件，提取带宽值
    bandwidth_val=$(cat ceph_iops_bandwidth_write.log |grep "Bandwidth (MB/sec):" | awk -F ':' '{print $2}')
    #通过查看ceph_iops_bandwidth_write.log文件，提取iops值
    iops_val=$(cat ceph_iops_bandwidth_write.log |grep "Average IOPS:" | awk -F ':' '{print $2}')
    #执行该benchmark脚本时，可能ceph_iops_bandwidth_write.log文件中还没有生成内容，为了避免采集数据时出现参数值空，导致调优失败的情况，此处反复读取日志文件，如果读取日志失败，每次等待3s，超出10次还没有读取到，会直接退出，调优失败。
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


```
## ceph_client.yaml
执行atune调优命令atune-adm tuning --project ceph --detail ceph_client.yaml时会用到该脚本，ceph_client.yaml文件会指明benchmark脚本的路径，及如何执行benchmark脚本来获取基线数据。yaml文件中需要设置ceph性能评估指标，主要关注带宽和IOPS两个性能指标，每个指标的weight代表该指标权重。
ceph_client.yaml源码如下：
```bash
project: "ceph"
engine: "gbrt"
iterations: 30
random_starts: 2

#此处的PATH路径是可替换参数，在执行prepare.sh脚本后，会替换为当前所在路径
benchmark : "sh PATH/ceph_benchmark.sh"

#性能评估指标值的获取
evaluations :
    -
        name: "bandwidth"
        info:
            #$out为ceph_benchmark.sh脚本执行后的输出值，通过grep捕获benchmark脚本的输出值中bandwidth_val所在行的对应参数值
            get: "echo '$out' |grep 'bandwidth_val'| awk '{print $3}'"
            type: "negative"
            weight: 50
    -
        name: "iops_val"
        info:
            #$out为ceph_benchmark.sh脚本执行后的输出值，通过grep捕获benchmark脚本的输出值中iops_val所在行的对应参数值
            get: "echo '$out' |grep 'iops_val'| awk '{print $3}'"
            type: "negative"
            weight: 50

```
## ceph_server.yaml
ceph_server.yaml文件是进行atune服务端调优的主要参数配置文件，包含ceph集群的调优参数，说明了各个参数的取值范围，获取参数值的方式和设置生效的方式。
ceph_server.yaml源码如下：
```bash
project: "ceph"
maxiterations: 100
startworkload: ""
stopworkload: ""
object :
    -
        name : "ceph.rbd_op_threads"
        info :
            desc : "The number of worker threads in the RBD client's thread pool."
            #执行get_ceph_param_info.sh脚本获取当前参数的对应值
            get : "sh PATH/get_ceph_param_info.sh rbd_op_threads"
            #将获取到的当前参数对应值应用到ceph集群的所有osd节点中，如果想要分发到特定的osd节点，可以将osd.*换为osd.1等
            set : "ceph tell osd.* injectargs --rbd_op_threads ${value}"
            needrestart : "false"
            type : "discrete"
            scope :
                - 1
                - 8
            step : 1
            items :
            dtype : "int"
    -
        name : "vm.swappiness"
        info :
          desc : "A larger value indicates that the swap partition is used more actively. A smaller value indicates that the memory is used more actively."
          get : "sysctl -n vm.swappiness"
          set : "sysctl -w vm.swappiness=${value}"
          needrestart : "false"
          type : "discrete"
          scope :
            - 0
            - 100
          step : 1
          items :
          dtype : "int"
    -
        name: "pid_max"
        info:
            desc: "A larger value indicates that the swap partition is used more actively. A smaller value indicates that the memory is used more actively."
            get: "cat /proc/sys/kernel/pid_max"
            set: "echo ${value} > /proc/sys/kernel/pid_max"
            needrestart: "false"
            type: "discrete"
            scope:
                - 4194304
                - 8388608
            step: 4194304
            items:
            dtype: "int"

```
## get_ceph_param_info.sh
该脚本在ceph_server.yaml文件中指定，会被atune服务调用，用来获取对应参数在ceph集群中的值，参与每一轮的迭代调优，筛选出最优值。
get_ceph_param_info.sh源码如下：
```bash
#!/bin/bash

# 检查参数个数
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <metric_name>"
    exit 1
fi

# 读取参数
METRIX_NAME=$1

# 获取 OSD 节点信息的第一个节点名称，ceph集群中各节点中的信息值是类似的，因此获取一个节点的参数值
NODE_NAME=$(ceph node ls | jq -r '.osd | keys[0]')

# 检查是否成功获取到节点名称
if [ -z "$NODE_NAME" ]; then
    echo "Failed to get the first node name."
    exit 1
fi

# 假设第一个节点的 OSD ID 列表中的第一个 OSD ID
OSD_ID=$(ceph node ls | jq -r ".osd[\"$NODE_NAME\"][0]")

# 检查是否成功获取到 OSD ID
if [ -z "$OSD_ID" ]; then
    echo "Failed to get the first OSD ID for node $NODE_NAME."
    exit 1
fi

# 执行 SSH 命令获取配置值
VALUE=$(ssh -q "${NODE_NAME}" "ceph daemon osd.${OSD_ID} config get ${METRIX_NAME}" | jq -r '. | values | .[]')

# 检查 SSH 命令是否执行成功
echo ${VALUE}
```
## prepare.sh
环境部署脚本，该脚本会计算当前文件夹所处的绝对路径，然后将该路径替换ceph_client.yaml和ceph_server.yaml中的PATH参数，保证ceph_benchmark.sh基线脚本可以正常执行，同时会将ceph_server.yaml部署到调优路径/etc/atuned/tuning/ceph/下，保证atune调优的正常执行。
prepare.sh源码如下：
```bash
#!/bin/sh

#获取当前脚本所处的绝对路径，赋值给变量path
path=$(
    cd "$(dirname "$0")"
    pwd
)
echo "path: ${path}"

#执行脚本后需要输入的两个参数PG_NUMBER，PGP_NUMBER
read -p "[INPUT] enter PG_NUMBER of testbench to used:" PG_NUMBER
read -p "[INPUT] enter PGP_NUMBER of testbench to used:" PGP_NUMBER

echo "[INFO] update the client and server yaml files"
#更新ceph_client.yaml文件中的PATH变量为当前所处绝对路径
sed -i "s#PATH#${path}#g" ${path}/ceph_client.yaml
#替换ceph_benchmark.sh文件中的PG_NUMBER为手动输入的值
sed -i "s#PG_NUMBER=.*#PG_NUMBER=$PG_NUMBER#g" ${path}/ceph_benchmark.sh
#更新ceph_server.yaml文件中的PATH变量为当前所处绝对路径
sed -i "s#PATH#${path}#g" ${path}/ceph_server.yaml

#ceph_server.yaml文件复制到ceph的调优路径/etc/atuned/tuning/ceph下，用于调优过程中读取ceph的参数值
if [ ! -d /etc/atuned/tuning/ceph ]; then
    mkdir /etc/atuned/tuning/ceph
fi
cp ${path}/ceph_server.yaml /etc/atuned/tuning/ceph/ceph_server.yaml


```