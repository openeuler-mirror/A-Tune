# 1.ceph环境准备
ceph环境部署后包含benchmark测试工具rados
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
Huawei12#$
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


将client节点上的密钥分发到各节点

```
for host in ceph1 ceph2 ceph3; do
  scp ceph.conf root@$host:/etc/ceph/ceph.conf
  scp ceph.client.admin.keyring root@$host:/etc/ceph/ceph.client.admin.keyring
  ssh root@$host "mkdir -p /var/lib/ceph/bootstrap-osd/"
  scp ceph.bootstrap-osd.keyring root@$host:/var/lib/ceph/bootstrap-osd/ceph.keyring
  ssh root@$host "chown -R ceph:ceph /var/lib/ceph/bootstrap-osd && chmod 600 /var/lib/ceph/bootstrap-osd/ceph.keyring"
done
```

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
##### 新创建磁盘分区

```
umount /dev/mapper/openeuler-home
e2fsck -f /dev/mapper/openeuler-home
resize2fs /dev/mapper/openeuler-home 20G
lvreduce -L 20G /dev/mapper/openeuler-home
mount /dev/mapper/openeuler-home /home
df -h /home
pvresize --setphysicalvolumesize  XG /dev/vda3
vgdisplay openeuler
lvcreate -n ceph-osd-03 -L 9G openeuler
ceph-volume lvm prepare --data /dev/openeuler/ceph-osd-03
```



在client节点上执行，对三个ceph节点分别执行如下命令，注意disk zap 操作会擦除磁盘上的所有数据，建议提前数据备份。osd create 操作会将该磁盘创建为 Ceph 集群中的 OSD 存储设备：
```bash
ceph-deploy disk zap ceph1 /dev/openeuler/ceph-osd-01
ceph-deploy osd create ceph1 --data /dev/openeuler/ceph-osd-01
ceph-deploy disk zap ceph2 /dev/openeuler/ceph-osd-02
ceph-deploy osd create ceph2 --data /dev/openeuler/ceph-osd-02
ceph-deploy disk zap ceph3 /dev/openeuler/ceph-osd-03
ceph-deploy osd create ceph3 --data /dev/openeuler/ceph-osd-03
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
