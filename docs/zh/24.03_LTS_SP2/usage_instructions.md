# 使用方法

用户可以通过命令行客户端atune-adm使用A-Tune提供的功能。本章介绍A-Tune客户端包含的功能和使用方法。

## 总体说明

- 使用A-Tune需要使用root权限。
- atune-adm支持的命令可以通过  **atune-adm help/--help/-h**  查询。
- define、update、undefine、collection、train、upgrade不支持远程执行。
- 命令格式中，\[ \] 表示参数可选，<\> 表示参数必选，具体参数由实际情况确定。

## 查询负载类型

### list

### 功能描述

查询系统当前支持的profile，以及当前处于active状态的profile。

### 命令格式

**atune-adm list**

### 使用示例

```sh
# atune-adm list 

Support profiles:
+------------------------------------------------+-----------+
| ProfileName                                    | Active    |
+================================================+===========+
| arm-native-android-container-robox             | false     |
+------------------------------------------------+-----------+
| basic-test-suite-euleros-baseline-fio          | false     |
+------------------------------------------------+-----------+
| basic-test-suite-euleros-baseline-lmbench      | false     |
+------------------------------------------------+-----------+
| basic-test-suite-euleros-baseline-netperf      | false     |
+------------------------------------------------+-----------+
| basic-test-suite-euleros-baseline-stream       | false     |
+------------------------------------------------+-----------+
| basic-test-suite-euleros-baseline-unixbench    | false     |
+------------------------------------------------+-----------+
| basic-test-suite-speccpu-speccpu2006           | false     |
+------------------------------------------------+-----------+
| basic-test-suite-specjbb-specjbb2015           | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-hdfs-dfsio-hdd                 | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-hdfs-dfsio-ssd                 | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-bayesian                 | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-kmeans                   | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-sql1                     | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-sql10                    | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-sql2                     | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-sql3                     | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-sql4                     | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-sql5                     | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-sql6                     | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-sql7                     | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-sql8                     | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-sql9                     | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-tersort                  | false     |
+------------------------------------------------+-----------+
| big-data-hadoop-spark-wordcount                | false     |
+------------------------------------------------+-----------+
| cloud-compute-kvm-host                         | false     |
+------------------------------------------------+-----------+
| database-mariadb-2p-tpcc-c3                    | false     |
+------------------------------------------------+-----------+
| database-mariadb-4p-tpcc-c3                    | false     |
+------------------------------------------------+-----------+
| database-mongodb-2p-sysbench                   | false     |
+------------------------------------------------+-----------+
| database-mysql-2p-sysbench-hdd                 | false     |
+------------------------------------------------+-----------+
| database-mysql-2p-sysbench-ssd                 | false     |
+------------------------------------------------+-----------+
| database-postgresql-2p-sysbench-hdd            | false     |
+------------------------------------------------+-----------+
| database-postgresql-2p-sysbench-ssd            | false     |
+------------------------------------------------+-----------+
| default-default                                | false     |
+------------------------------------------------+-----------+
| docker-mariadb-2p-tpcc-c3                      | false     |
+------------------------------------------------+-----------+
| docker-mariadb-4p-tpcc-c3                      | false     |
+------------------------------------------------+-----------+
| hpc-gatk4-human-genome                         | false     |
+------------------------------------------------+-----------+
| in-memory-database-redis-redis-benchmark       | false     |
+------------------------------------------------+-----------+
| middleware-dubbo-dubbo-benchmark               | false     |
+------------------------------------------------+-----------+
| storage-ceph-vdbench-hdd                       | false     |
+------------------------------------------------+-----------+
| storage-ceph-vdbench-ssd                       | false     |
+------------------------------------------------+-----------+
| virtualization-consumer-cloud-olc              | false     |
+------------------------------------------------+-----------+
| virtualization-mariadb-2p-tpcc-c3              | false     |
+------------------------------------------------+-----------+
| virtualization-mariadb-4p-tpcc-c3              | false     |
+------------------------------------------------+-----------+
| web-apache-traffic-server-spirent-pingpo       | false     |
+------------------------------------------------+-----------+
| web-nginx-http-long-connection                 | true      |
+------------------------------------------------+-----------+
| web-nginx-https-short-connection               | false     |
+------------------------------------------------+-----------+

```

>![](./public_sys-resources/icon-note.gif) **说明：**
>Active为true表示当前激活的profile，示例表示当前激活的profile是web-nginx-http-long-connection。  

## 分析负载类型并自优化

### analysis

### 功能描述

采集系统的实时统计数据进行负载类型识别，并进行自动优化。

### 命令格式

**atune-adm analysis**  \[OPTIONS\]

### 参数说明

- OPTIONS

    <a name="table17341193974513"></a>

    <table><thead align="left"><tr id="row11341739154514"><th class="cellrowborder" valign="top" width="23.87%" id="mcps1.1.3.1.1"><p id="p3341183964511"><a name="p3341183964511"></a><a name="p3341183964511"></a>参数</p>
    </th>
    <th class="cellrowborder" valign="top" width="76.13%" id="mcps1.1.3.1.2"><p id="p73410399457"><a name="p73410399457"></a><a name="p73410399457"></a>描述</p>
    </th>
    </tr>
    </thead>
    <tbody><tr id="row334110395452"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="p9341639104517"><a name="p9341639104517"></a><a name="p9341639104517"></a>--model, -m</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="p23414394459"><a name="p23414394459"></a><a name="p23414394459"></a>用户自训练产生的新模型</p>
    </td>
    </tr>
    <tr id="row334110395452"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="p9341639104517"><a name="p9341639104517"></a><a name="p9341639104517"></a>--characterization, -c</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="p23414394459"><a name="p23414394459"></a><a name="p23414394459"></a>使用默认的模型进行应用识别，不进行自动优化</p>
    </td>
    </tr>
    <tr id="row334110395452"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="p9341639104517"><a name="p9341639104517"></a><a name="p9341639104517"></a>--times value, -t value</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="p23414394459"><a name="p23414394459"></a><a name="p23414394459"></a>指定收集数据的时长</p>
    </td>
    </tr>
    <tr id="row334110395452"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="p9341639104517"><a name="p9341639104517"></a><a name="p9341639104517"></a>--script value, -s value</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="p23414394459"><a name="p23414394459"></a><a name="p23414394459"></a>指定需要运行的文件</p>
    </td>
    </tr>
    </tbody>
    </table>

### 使用示例

- 使用默认的模型进行应用识别

    ```sh
    # atune-adm analysis --characterization
    ```

- 使用默认的模型进行应用识别，并进行自动优化

    ```sh
    # atune-adm analysis
    ```

- 使用自训练的模型进行应用识别

    ```sh
    # atune-adm analysis --model /usr/libexec/atuned/analysis/models/new-model.m
    ```

## 自定义模型

A-Tune支持用户定义并学习新模型。定义新模型的操作流程如下：

1. 用define命令定义一个新应用的profile
2. 用collection命令收集应用对应的系统数据
3. 用train命令训练得到模型

### define

### 功能描述

添加用户自定义的应用场景，及对应的profile优化项。

### 命令格式

**atune-adm define**  \<service_type> \<application_name> \<scenario_name> \<profile_path>

### 使用示例

新增一个profile，service_type的名称为test_service，application_name的名称为test_app，scenario_name的名称为test_scenario，优化项的配置文件为example.conf。

```sh
# atune-adm define test_service test_app test_scenario ./example.conf
```

example.conf 可以参考如下方式书写（以下各优化项非必填，仅供参考），也可通过**atune-adm info**查看已有的profile是如何书写的。

```Conf
 [main]
 # list its parent profile
 [kernel_config]
 # to change the kernel config
 [bios]
 # to change the bios config
 [bootloader.grub2]
 # to change the grub2 config
 [sysfs]
 # to change the /sys/* config
 [systemctl]
 # to change the system service status
 [sysctl]
 # to change the /proc/sys/* config
 [script]
 # the script extension of cpi
 [ulimit]
 # to change the resources limit of user
 [schedule_policy]
 # to change the schedule policy
 [check]
 # check the environment
 [tip]
 # the recommended optimization, which should be performed manunaly
```

### collection

### 功能描述

采集业务运行时系统的全局资源使用情况以及OS的各项状态信息，并将收集的结果保存到csv格式的输出文件中，作为模型训练的输入数据集。

>![](./public_sys-resources/icon-note.gif) **说明：**
>
>- 本命令依赖采样工具perf，mpstat，vmstat，iostat，sar。
>- CPU型号目前仅支持鲲鹏920，可通过dmidecode -t processor检查CPU型号。  

### 命令格式

**atune-adm collection**  <OPTIONS\>

### 参数说明

- OPTIONS

    <a name="zh-cn_topic_0210923698_table960915119119"></a>
    <table><thead align="left"><tr id="zh-cn_topic_0210923698_row13645013114"><th class="cellrowborder" valign="top" width="23.87%" id="mcps1.1.3.1.1"><p id="zh-cn_topic_0210923698_p176451311914"><a name="zh-cn_topic_0210923698_p176451311914"></a><a name="zh-cn_topic_0210923698_p176451311914"></a>参数</p>
    </th>
    <th class="cellrowborder" valign="top" width="76.13%" id="mcps1.1.3.1.2"><p id="zh-cn_topic_0210923698_p1364511211"><a name="zh-cn_topic_0210923698_p1364511211"></a><a name="zh-cn_topic_0210923698_p1364511211"></a>描述</p>
    </th>
    </tr>
    </thead>
    <tbody><tr id="zh-cn_topic_0210923698_row19645141112"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923698_p2645611710"><a name="zh-cn_topic_0210923698_p2645611710"></a><a name="zh-cn_topic_0210923698_p2645611710"></a>--filename, -f</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923698_p10645512017"><a name="zh-cn_topic_0210923698_p10645512017"></a><a name="zh-cn_topic_0210923698_p10645512017"></a>生成的用于训练的csv文件名：<em id="i14756164914010"><a name="i14756164914010"></a><a name="i14756164914010"></a>名称-时间戳</em>.csv</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923698_row564581117"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923698_p15645911616"><a name="zh-cn_topic_0210923698_p15645911616"></a><a name="zh-cn_topic_0210923698_p15645911616"></a>--output_path, -o</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923698_p106451918120"><a name="zh-cn_topic_0210923698_p106451918120"></a><a name="zh-cn_topic_0210923698_p106451918120"></a>生成的csv文件的存放路径，需提供绝对路径</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923698_row8645711115"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923698_p14645713117"><a name="zh-cn_topic_0210923698_p14645713117"></a><a name="zh-cn_topic_0210923698_p14645713117"></a>--disk, -b</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923698_p464519116110"><a name="zh-cn_topic_0210923698_p464519116110"></a><a name="zh-cn_topic_0210923698_p464519116110"></a>业务运行时实际使用的磁盘，如/dev/sda</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923698_row6645111714"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923698_p106451817111"><a name="zh-cn_topic_0210923698_p106451817111"></a><a name="zh-cn_topic_0210923698_p106451817111"></a>--network, -n</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923698_p206451911611"><a name="zh-cn_topic_0210923698_p206451911611"></a><a name="zh-cn_topic_0210923698_p206451911611"></a>业务运行时使用的网络接口，如eth0</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923698_row14645219112"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923698_p9645191811"><a name="zh-cn_topic_0210923698_p9645191811"></a><a name="zh-cn_topic_0210923698_p9645191811"></a>--app_type, -t</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923698_p16450117114"><a name="zh-cn_topic_0210923698_p16450117114"></a><a name="zh-cn_topic_0210923698_p16450117114"></a>标记业务的应用类型，作为训练时使用的标签</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923698_row76452118115"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923698_p96451114116"><a name="zh-cn_topic_0210923698_p96451114116"></a><a name="zh-cn_topic_0210923698_p96451114116"></a>--duration, -d</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="p3205204519273"><a name="p3205204519273"></a><a name="p3205204519273"></a>业务运行时采集数据的时间，单位秒，默认采集时间1200秒</p>
    </td>
    </tr>
    <tr id="row17981103311169"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="p698223313169"><a name="p698223313169"></a><a name="p698223313169"></a>--interval，-i</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="p12982633141617"><a name="p12982633141617"></a><a name="p12982633141617"></a><span>采集数据的时间间隔，单位秒，默认采集间隔5秒</span></p>
    </td>
    </tr>
    </tbody>
    </table>

### 使用示例

```sh
# atune-adm collection --filename name --interval 5 --duration 1200 --output_path /home/data --disk sda --network eth0 --app_type test_service-test_app-test_scenario 
```

> 说明：
>
> 实例中定义了每隔5秒收集一次数据，一共收集1200秒；采集后的数据存放在/home/data目录下名称为name的文件中，业务的应用类型是通过atune-adm define指定的业务类型，这里为test_service-test_app-test_scenario
> 采集间隔和采集时间都可以通过上述选项指定时长。
>
### train

### 功能描述

使用采集的数据进行模型的训练。训练时至少采集两种应用类型的数据，否则训练会出错。

### 命令格式

**atune-adm train**  <OPTIONS\>

### 参数说明

- OPTIONS

    <a name="zh-cn_topic_0210923699_table847613161310"></a>
    <table><thead align="left"><tr id="zh-cn_topic_0210923699_row349814169120"><th class="cellrowborder" valign="top" width="23.87%" id="mcps1.1.3.1.1"><p id="zh-cn_topic_0210923699_p1549841614116"><a name="zh-cn_topic_0210923699_p1549841614116"></a><a name="zh-cn_topic_0210923699_p1549841614116"></a>参数</p>
    </th>
    <th class="cellrowborder" valign="top" width="76.13%" id="mcps1.1.3.1.2"><p id="zh-cn_topic_0210923699_p84988168119"><a name="zh-cn_topic_0210923699_p84988168119"></a><a name="zh-cn_topic_0210923699_p84988168119"></a>描述</p>
    </th>
    </tr>
    </thead>
    <tbody><tr id="zh-cn_topic_0210923699_row13499181612118"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923699_p24993163119"><a name="zh-cn_topic_0210923699_p24993163119"></a><a name="zh-cn_topic_0210923699_p24993163119"></a>--data_path, -d</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923699_p134991316818"><a name="zh-cn_topic_0210923699_p134991316818"></a><a name="zh-cn_topic_0210923699_p134991316818"></a>存放模型训练所需的csv文件的目录</p>
    </td>
    </tr>
    <tr id="zh-cn_topic_0210923699_row149914161115"><td class="cellrowborder" valign="top" width="23.87%" headers="mcps1.1.3.1.1 "><p id="zh-cn_topic_0210923699_p14991516914"><a name="zh-cn_topic_0210923699_p14991516914"></a><a name="zh-cn_topic_0210923699_p14991516914"></a>--output_file, -o</p>
    </td>
    <td class="cellrowborder" valign="top" width="76.13%" headers="mcps1.1.3.1.2 "><p id="zh-cn_topic_0210923699_p049916166114"><a name="zh-cn_topic_0210923699_p049916166114"></a><a name="zh-cn_topic_0210923699_p049916166114"></a>训练生成的新模型</p>
    </td>
    </tr>
    </tbody>
    </table>

### 使用示例

使用data目录下的csv文件作为训练输入，生成的新模型new-model.m存放在model目录下。

```bash
# atune-adm train --data_path /home/data --output_file /usr/libexec/atuned/analysis/models/new-model.m 
```

### undefine

### 功能描述

删除用户自定义的profile。

### 命令格式

**atune-adm undefine**  <profile\>

### 使用示例

删除自定义的profile。

```bash
# atune-adm undefine test_service-test_app-test_scenario
```

## 查询profile

### info

### 功能描述

查看对应的profile内容。

### 命令格式

**atune-adm info**  <profile\>

### 使用示例

查看web-nginx-http-long-connection的profile内容：

```bash
# atune-adm info web-nginx-http-long-connection

*** web-nginx-http-long-connection:

#
# nginx http long connection A-Tune configuration
#
[main]
include = default-default

[kernel_config]
#TODO CONFIG

[bios]
#TODO CONFIG

[bootloader.grub2]
iommu.passthrough = 1

[sysfs]
#TODO CONFIG

[systemctl]
sysmonitor = stop
irqbalance = stop

[sysctl]
fs.file-max = 6553600
fs.suid_dumpable = 1
fs.aio-max-nr = 1048576
kernel.shmmax = 68719476736
kernel.shmall = 4294967296
kernel.shmmni = 4096
kernel.sem = 250 32000 100 128
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_syncookies = 1
net.ipv4.ip_local_port_range = 1024     65500
net.ipv4.tcp_max_tw_buckets = 5000
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 262144
net.ipv4.tcp_max_orphans = 262144
net.ipv4.tcp_max_syn_backlog = 262144
net.ipv4.tcp_timestamps = 0
net.ipv4.tcp_synack_retries = 1
net.ipv4.tcp_syn_retries = 1
net.ipv4.tcp_fin_timeout = 1
net.ipv4.tcp_keepalive_time = 60
net.ipv4.tcp_mem =  362619      483495   725238
net.ipv4.tcp_rmem = 4096         87380   6291456
net.ipv4.tcp_wmem = 4096         16384   4194304
net.core.wmem_default = 8388608
net.core.rmem_default = 8388608
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216

[script]
prefetch = off
ethtool =  -X {network} hfunc toeplitz

[ulimit]
{user}.hard.nofile = 102400
{user}.soft.nofile = 102400

[schedule_policy]
#TODO CONFIG

[check]
#TODO CONFIG

[tip]
SELinux provides extra control and security features to linux kernel. Disabling SELinux will improve the performance but may cause security risks. = kernel
disable the nginx log = application
```

## 更新profile

用户根据需要更新已有profile。

### update

### 功能描述

将已有profile中原来的优化项更新为new.conf中的内容。

### 命令格式

**atune-adm update**  <profile\> <profile_path\>

### 使用示例

更新名为test_service-test_app-test_scenario的profile优化项为new.conf。

```bash
# atune-adm update test_service-test_app-test_scenario ./new.conf
```

## 激活profile

### profile

### 功能描述

手动激活profile，使其处于active状态。

### 命令格式

**atune-adm profile** <profile\>

### 参数说明

profile名参考list命令查询结果。

### 使用示例

激活web-nginx-http-long-connection对应的profile配置。

```sh
# atune-adm profile web-nginx-http-long-connection
```

## 回滚profile

### rollback

### 功能描述

回退当前的配置到系统的初始配置。

### 命令格式

**atune-adm rollback**

### 使用示例

```sh
# atune-adm rollback
```

## 更新数据库

### upgrade

### 功能描述

更新系统的数据库。

### 命令格式

**atune-adm upgrade**  <DB\_FILE\>

### 参数说明

- DB\_FILE

    新的数据库文件路径

### 使用示例

数据库更新为new\_sqlite.db。

```sh
# atune-adm upgrade ./new_sqlite.db
```

## 系统信息查询

### check

### 功能描述

检查系统当前的cpu、bios、os、网卡等信息。

### 命令格式

**atune-adm check**

### 使用示例

```sh
# atune-adm check
 cpu information:
     cpu:0   version: Kunpeng 920-6426  speed: 2600000000 HZ   cores: 64
     cpu:1   version: Kunpeng 920-6426  speed: 2600000000 HZ   cores: 64
 system information:
     DMIBIOSVersion: 0.59
     OSRelease: 4.19.36-vhulk1906.3.0.h356.eulerosv2r8.aarch64
 network information:
     name: eth0              product: HNS GE/10GE/25GE RDMA Network Controller
     name: eth1              product: HNS GE/10GE/25GE Network Controller
     name: eth2              product: HNS GE/10GE/25GE RDMA Network Controller
     name: eth3              product: HNS GE/10GE/25GE Network Controller
     name: eth4              product: HNS GE/10GE/25GE RDMA Network Controller
     name: eth5              product: HNS GE/10GE/25GE Network Controller
     name: eth6              product: HNS GE/10GE/25GE RDMA Network Controller
     name: eth7              product: HNS GE/10GE/25GE Network Controller
     name: docker0           product:
```

## 参数自调优

A-Tune提供了最佳配置的自动搜索能力，免去人工反复做参数调整、性能评价的调优过程，极大地提升最优配置的搜寻效率。

### tuning

### 功能描述

使用指定的项目文件对参数进行动态空间的搜索，找到当前环境配置下的最优解。

### 命令格式

> [!NOTE]说明 
>在运行命令前，需要满足如下条件：  
>
>（1） 服务端的yaml配置文件已经编辑完成并放置于 atuned服务下的**/etc/atuned/tuning/**目录中。
>（2） 客户端的yaml配置文件已经编辑完成并放置于atuned客户端任意目录下。

**atune-adm tuning**  \[OPTIONS\] <PROJECT\_YAML\>

### 参数说明

- OPTIONS

    <a name="table128011465441"></a>

    <table><thead align="left"><tr id="row16801164620446"><th class="cellrowborder" valign="top" width="50%" id="mcps1.1.3.1.1"><p id="p4801046114412"><a name="p4801046114412"></a><a name="p4801046114412"></a>参数</p>
    </th>
    <th class="cellrowborder" valign="top" width="50%" id="mcps1.1.3.1.2"><p id="p1280184654418"><a name="p1280184654418"></a><a name="p1280184654418"></a>描述</p>
    </th>
    </tr>
    </thead>
    <tbody><tr id="row080110466442"><td class="cellrowborder" valign="top" width="50%" headers="mcps1.1.3.1.1 "><p id="p108011346154411"><a name="p108011346154411"></a><a name="p108011346154411"></a>--restore, -r</p>
    </td>
    <td class="cellrowborder" valign="top" width="50%" headers="mcps1.1.3.1.2 "><p id="p1980144614414"><a name="p1980144614414"></a><a name="p1980144614414"></a>恢复tuning优化前的初始配置</p>
    </td>
    </tr>
    <tr id="row88018467448"><td class="cellrowborder" valign="top" width="50%" headers="mcps1.1.3.1.1 "><p id="p78011346164417"><a name="p78011346164417"></a><a name="p78011346164417"></a>--project, -p</p>
    </td>
    <td class="cellrowborder" valign="top" width="50%" headers="mcps1.1.3.1.2 "><p id="p10802114624412"><a name="p10802114624412"></a><a name="p10802114624412"></a>指定需要恢复的yaml文件中的项目名称</p>
    </td>
    </tr>
    <tr id="row88018467448"><td class="cellrowborder" valign="top" width="50%" headers="mcps1.1.3.1.1 "><p id="p78011346164417"><a name="p78011346164417"></a><a name="p78011346164417"></a>--restart, -c</p>
    </td>
    <td class="cellrowborder" valign="top" width="50%" headers="mcps1.1.3.1.2 "><p id="p10802114624412"><a name="p10802114624412"></a><a name="p10802114624412"></a>基于历史调优结果进行调优</p>
    </td>
    </tr>
    <tr id="row88018467448"><td class="cellrowborder" valign="top" width="50%" headers="mcps1.1.3.1.1 "><p id="p78011346164417"><a name="p78011346164417"></a><a name="p78011346164417"></a>--detail, -d</p>
    </td>
    <td class="cellrowborder" valign="top" width="50%" headers="mcps1.1.3.1.2 "><p id="p10802114624412"><a name="p10802114624412"></a><a name="p10802114624412"></a>打印tuning过程的详细信息</p>
    </td>
    </tr>
    </tbody>
    </table>

    >![](./public_sys-resources/icon-note.gif) **说明：**
    >当使用参数时，-p参数后需要跟具体的项目名称且必须指定该项目yaml文件。  

- PROJECT\_YAML：客户端yaml配置文件。

### 配置说明

**表 1**  服务端yaml文件

<a name="table9580161612454"></a>
<table><thead align="left"><tr id="row45801216104518"><th class="cellrowborder" valign="top" width="16.84%" id="mcps1.2.5.1.1"><p id="p758011611453"><a name="p758011611453"></a><a name="p758011611453"></a><strong id="b1658071624516"><a name="b1658071624516"></a><a name="b1658071624516"></a>配置名称</strong></p>
</th>
<th class="cellrowborder" valign="top" width="19.97%" id="mcps1.2.5.1.2"><p id="p13580916114518"><a name="p13580916114518"></a><a name="p13580916114518"></a><strong id="b65809164454"><a name="b65809164454"></a><a name="b65809164454"></a>配置说明</strong></p>
</th>
<th class="cellrowborder" valign="top" width="15.72%" id="mcps1.2.5.1.3"><p id="p7580111618455"><a name="p7580111618455"></a><a name="p7580111618455"></a><strong id="b15801516154520"><a name="b15801516154520"></a><a name="b15801516154520"></a>参数类型</strong></p>
</th>
<th class="cellrowborder" valign="top" width="47.47%" id="mcps1.2.5.1.4"><p id="p1258071610456"><a name="p1258071610456"></a><a name="p1258071610456"></a><strong id="b17580516174511"><a name="b17580516174511"></a><a name="b17580516174511"></a>取值范围</strong></p>
</th>
</tr>
</thead>
<tbody><tr id="row1858051613457"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p16580121634512"><a name="p16580121634512"></a><a name="p16580121634512"></a>project</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p175808167455"><a name="p175808167455"></a><a name="p175808167455"></a>项目名称。</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p1258061644510"><a name="p1258061644510"></a><a name="p1258061644510"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p17580121684515"><a name="p17580121684515"></a><a name="p17580121684515"></a>-</p>
</td>
</tr>
<tr id="row65800162454"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p3580101619450"><a name="p3580101619450"></a><a name="p3580101619450"></a>startworkload</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p1158041617457"><a name="p1158041617457"></a><a name="p1158041617457"></a>待调优服务的启动脚本。</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p2580316124517"><a name="p2580316124517"></a><a name="p2580316124517"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p165801116124518"><a name="p165801116124518"></a><a name="p165801116124518"></a>-</p>
</td>
</tr>
<tr id="row2580121624516"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p558015165459"><a name="p558015165459"></a><a name="p558015165459"></a>stopworkload</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p3580101614453"><a name="p3580101614453"></a><a name="p3580101614453"></a>待调优服务的停止脚本。</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p1158051664512"><a name="p1158051664512"></a><a name="p1158051664512"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p19580141614458"><a name="p19580141614458"></a><a name="p19580141614458"></a>-</p>
</td>
</tr>
<tr id="row195801316144516"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p1658011169457"><a name="p1658011169457"></a><a name="p1658011169457"></a>maxiterations</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p3580151613450"><a name="p3580151613450"></a><a name="p3580151613450"></a>最大调优迭代次数，用于限制客户端的迭代次数。一般来说，调优迭代次数越多，优化效果越好，但所需时间越长。用户必须根据实际的业务场景进行配置。</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p105801716174518"><a name="p105801716174518"></a><a name="p105801716174518"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p85805162457"><a name="p85805162457"></a><a name="p85805162457"></a>&gt;10</p>
</td>
</tr>
<tr id="row1458010169452"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p1058018160452"><a name="p1058018160452"></a><a name="p1058018160452"></a>object</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p1758011161451"><a name="p1758011161451"></a><a name="p1758011161451"></a>需要调节的参数项及信息。</p>
<p id="p2058081616452"><a name="p2058081616452"></a><a name="p2058081616452"></a>object 配置项请参见<a href="#table9803156161910">表2</a>。</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p35801169454"><a name="p35801169454"></a><a name="p35801169454"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p8580111694510"><a name="p8580111694510"></a><a name="p8580111694510"></a>-</p>
</td>
</tr>
</tbody>
</table>

**表 2**  object项配置说明

<a name="table9803156161910"></a>

<table><thead align="left"><tr id="row3800656151910"><th class="cellrowborder" valign="top" width="16.98%" id="mcps1.2.5.1.1"><p id="p3799185621910"><a name="p3799185621910"></a><a name="p3799185621910"></a><strong id="b279913562195"><a name="b279913562195"></a><a name="b279913562195"></a>配置名称</strong></p>
</th>
<th class="cellrowborder" valign="top" width="20.26%" id="mcps1.2.5.1.2"><p id="p117991565191"><a name="p117991565191"></a><a name="p117991565191"></a><strong id="b279975618198"><a name="b279975618198"></a><a name="b279975618198"></a>配置说明</strong></p>
</th>
<th class="cellrowborder" valign="top" width="15.39%" id="mcps1.2.5.1.3"><p id="p479915569196"><a name="p479915569196"></a><a name="p479915569196"></a><strong id="b179965691915"><a name="b179965691915"></a><a name="b179965691915"></a>参数类型</strong></p>
</th>
<th class="cellrowborder" valign="top" width="47.370000000000005%" id="mcps1.2.5.1.4"><p id="p18799135691918"><a name="p18799135691918"></a><a name="p18799135691918"></a><strong id="b779925614195"><a name="b779925614195"></a><a name="b779925614195"></a>取值范围</strong></p>
</th>
</tr>
</thead>
<tbody><tr id="row118001856111913"><td class="cellrowborder" valign="top" width="16.98%" headers="mcps1.2.5.1.1 "><p id="p3800115661916"><a name="p3800115661916"></a><a name="p3800115661916"></a>name</p>
</td>
<td class="cellrowborder" valign="top" width="20.26%" headers="mcps1.2.5.1.2 "><p id="p128005569191"><a name="p128005569191"></a><a name="p128005569191"></a>待调参数名称</p>
</td>
<td class="cellrowborder" valign="top" width="15.39%" headers="mcps1.2.5.1.3 "><p id="p4800256101910"><a name="p4800256101910"></a><a name="p4800256101910"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%" headers="mcps1.2.5.1.4 "><p id="p380015681919"><a name="p380015681919"></a><a name="p380015681919"></a>-</p>
</td>
</tr>
<tr id="row1480055611196"><td class="cellrowborder" valign="top" width="16.98%" headers="mcps1.2.5.1.1 "><p id="p2080075691918"><a name="p2080075691918"></a><a name="p2080075691918"></a>desc</p>
</td>
<td class="cellrowborder" valign="top" width="20.26%" headers="mcps1.2.5.1.2 "><p id="p128001256111918"><a name="p128001256111918"></a><a name="p128001256111918"></a>待调参数描述</p>
</td>
<td class="cellrowborder" valign="top" width="15.39%" headers="mcps1.2.5.1.3 "><p id="p880019566191"><a name="p880019566191"></a><a name="p880019566191"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%" headers="mcps1.2.5.1.4 "><p id="p78004562190"><a name="p78004562190"></a><a name="p78004562190"></a>-</p>
</td>
</tr>
<tr id="row1680018561195"><td class="cellrowborder" valign="top" width="16.98%" headers="mcps1.2.5.1.1 "><p id="p2080095621913"><a name="p2080095621913"></a><a name="p2080095621913"></a>get</p>
</td>
<td class="cellrowborder" valign="top" width="20.26%" headers="mcps1.2.5.1.2 "><p id="p9800256131914"><a name="p9800256131914"></a><a name="p9800256131914"></a>查询参数值的脚本</p>
</td>
<td class="cellrowborder" valign="top" width="15.39%" headers="mcps1.2.5.1.3 "><p id="p480085615191"><a name="p480085615191"></a><a name="p480085615191"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%" headers="mcps1.2.5.1.4 "><p id="p15800656201915"><a name="p15800656201915"></a><a name="p15800656201915"></a>-</p>
</td>
</tr>
<tr id="row17801165613192"><td class="cellrowborder" valign="top" width="16.98%" headers="mcps1.2.5.1.1 "><p id="p1880085631913"><a name="p1880085631913"></a><a name="p1880085631913"></a>set</p>
</td>
<td class="cellrowborder" valign="top" width="20.26%" headers="mcps1.2.5.1.2 "><p id="p168006565198"><a name="p168006565198"></a><a name="p168006565198"></a>设置参数值的脚本</p>
</td>
<td class="cellrowborder" valign="top" width="15.39%" headers="mcps1.2.5.1.3 "><p id="p1280035651911"><a name="p1280035651911"></a><a name="p1280035651911"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%" headers="mcps1.2.5.1.4 "><p id="p68018563195"><a name="p68018563195"></a><a name="p68018563195"></a>-</p>
</td>
</tr>
<tr id="row180175621919"><td class="cellrowborder" valign="top" width="16.98%" headers="mcps1.2.5.1.1 "><p id="p6801145621915"><a name="p6801145621915"></a><a name="p6801145621915"></a>needrestart</p>
</td>
<td class="cellrowborder" valign="top" width="20.26%" headers="mcps1.2.5.1.2 "><p id="p480111568197"><a name="p480111568197"></a><a name="p480111568197"></a>参数生效是否需要重启业务</p>
</td>
<td class="cellrowborder" valign="top" width="15.39%" headers="mcps1.2.5.1.3 "><p id="p8801155613194"><a name="p8801155613194"></a><a name="p8801155613194"></a>枚举</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%" headers="mcps1.2.5.1.4 "><p id="p10801125615191"><a name="p10801125615191"></a><a name="p10801125615191"></a>"true", "false"</p>
</td>
</tr>
<tr id="row180118564191"><td class="cellrowborder" valign="top" width="16.98%" headers="mcps1.2.5.1.1 "><p id="p98015562190"><a name="p98015562190"></a><a name="p98015562190"></a>type</p>
</td>
<td class="cellrowborder" valign="top" width="20.26%" headers="mcps1.2.5.1.2 "><p id="p3801195681916"><a name="p3801195681916"></a><a name="p3801195681916"></a>参数的类型，目前支持discrete, continuous两种类型，对应离散型、连续型参数</p>
</td>
<td class="cellrowborder" valign="top" width="15.39%" headers="mcps1.2.5.1.3 "><p id="p17801195619197"><a name="p17801195619197"></a><a name="p17801195619197"></a>枚举</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%" headers="mcps1.2.5.1.4 "><p id="p9801856171916"><a name="p9801856171916"></a><a name="p9801856171916"></a>"discrete", "continuous"</p>
</td>
</tr>
<tr id="row1480275691918"><td class="cellrowborder" valign="top" width="16.98%" headers="mcps1.2.5.1.1 "><p id="p78019565194"><a name="p78019565194"></a><a name="p78019565194"></a>dtype</p>
</td>
<td class="cellrowborder" valign="top" width="20.26%" headers="mcps1.2.5.1.2 "><p id="p17801756101914"><a name="p17801756101914"></a><a name="p17801756101914"></a>该参数仅在type为discrete类型时配置，目前支持int, float, string类型</p>
</td>
<td class="cellrowborder" valign="top" width="15.39%" headers="mcps1.2.5.1.3 "><p id="p180145611193"><a name="p180145611193"></a><a name="p180145611193"></a>枚举</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%" headers="mcps1.2.5.1.4 "><p id="p7801956171913"><a name="p7801956171913"></a><a name="p7801956171913"></a>int, float, string</p>
</td>
</tr>
<tr id="row280235612194"><td class="cellrowborder" valign="top" width="16.98%" headers="mcps1.2.5.1.1 "><p id="p78027569198"><a name="p78027569198"></a><a name="p78027569198"></a>scope</p>
</td>
<td class="cellrowborder" valign="top" width="20.26%" headers="mcps1.2.5.1.2 "><p id="p180235617196"><a name="p180235617196"></a><a name="p180235617196"></a>参数设置范围，仅在type为discrete且dtype为int或float时或者type为continuous时生效</p>
</td>
<td class="cellrowborder" valign="top" width="15.39%" headers="mcps1.2.5.1.3 "><p id="p1780215617191"><a name="p1780215617191"></a><a name="p1780215617191"></a>整型/浮点型</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%" headers="mcps1.2.5.1.4 "><p id="p1680255641916"><a name="p1680255641916"></a><a name="p1680255641916"></a>用户自定义，取值在该参数的合法范围</p>
</td>
</tr>
<tr id="row138022565199"><td class="cellrowborder" valign="top" width="16.98%" headers="mcps1.2.5.1.1 "><p id="p880265681911"><a name="p880265681911"></a><a name="p880265681911"></a>step</p>
</td>
<td class="cellrowborder" valign="top" width="20.26%" headers="mcps1.2.5.1.2 "><p id="p6802256161918"><a name="p6802256161918"></a><a name="p6802256161918"></a>参数值步长，dtype为int或float时使用</p>
</td>
<td class="cellrowborder" valign="top" width="15.39%" headers="mcps1.2.5.1.3 "><p id="p198021156141918"><a name="p198021156141918"></a><a name="p198021156141918"></a>整型/浮点型</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%" headers="mcps1.2.5.1.4 "><p id="p1180265619195"><a name="p1180265619195"></a><a name="p1180265619195"></a>用户自定义</p>
</td>
</tr>
<tr id="row8802175611912"><td class="cellrowborder" valign="top" width="16.98%" headers="mcps1.2.5.1.1 "><p id="p2802205614195"><a name="p2802205614195"></a><a name="p2802205614195"></a>items</p>
</td>
<td class="cellrowborder" valign="top" width="20.26%" headers="mcps1.2.5.1.2 "><p id="p5802105681916"><a name="p5802105681916"></a><a name="p5802105681916"></a>参数值在scope定义范围之外的枚举值，dtype为int或float时使用</p>
</td>
<td class="cellrowborder" valign="top" width="15.39%" headers="mcps1.2.5.1.3 "><p id="p28025564191"><a name="p28025564191"></a><a name="p28025564191"></a>整型/浮点型</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%" headers="mcps1.2.5.1.4 "><p id="p980211562191"><a name="p980211562191"></a><a name="p980211562191"></a>用户自定义，取值在该参数的合法范围</p>
</td>
</tr>
<tr id="row188031256171916"><td class="cellrowborder" valign="top" width="16.98%" headers="mcps1.2.5.1.1 "><p id="p14802165641912"><a name="p14802165641912"></a><a name="p14802165641912"></a>options</p>
</td>
<td class="cellrowborder" valign="top" width="20.26%" headers="mcps1.2.5.1.2 "><p id="p17802656201916"><a name="p17802656201916"></a><a name="p17802656201916"></a>参数值的枚举范围，dtype为string时使用</p>
</td>
<td class="cellrowborder" valign="top" width="15.39%" headers="mcps1.2.5.1.3 "><p id="p198025562197"><a name="p198025562197"></a><a name="p198025562197"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.370000000000005%" headers="mcps1.2.5.1.4 "><p id="p78039562198"><a name="p78039562198"></a><a name="p78039562198"></a>用户自定义，取值在该参数的合法范围</p>
</td>
</tr>
</tbody>
</table>

**表 3**  客户端yaml文件配置说明

<a name="table114320101924"></a>

<table><thead align="left"><tr id="row84321410123"><th class="cellrowborder" valign="top" width="16.84%" id="mcps1.2.5.1.1"><p id="p7432201016216"><a name="p7432201016216"></a><a name="p7432201016216"></a><strong id="b643212101122"><a name="b643212101122"></a><a name="b643212101122"></a>配置名称</strong></p>
</th>
<th class="cellrowborder" valign="top" width="19.97%" id="mcps1.2.5.1.2"><p id="p54328101323"><a name="p54328101323"></a><a name="p54328101323"></a><strong id="b94321810524"><a name="b94321810524"></a><a name="b94321810524"></a>配置说明</strong></p>
</th>
<th class="cellrowborder" valign="top" width="15.72%" id="mcps1.2.5.1.3"><p id="p20432191016216"><a name="p20432191016216"></a><a name="p20432191016216"></a><strong id="b243212101218"><a name="b243212101218"></a><a name="b243212101218"></a>参数类型</strong></p>
</th>
<th class="cellrowborder" valign="top" width="47.47%" id="mcps1.2.5.1.4"><p id="p3432171020211"><a name="p3432171020211"></a><a name="p3432171020211"></a><strong id="b134321910621"><a name="b134321910621"></a><a name="b134321910621"></a>取值范围</strong></p>
</th>
</tr>
</thead>
<tbody><tr id="row104321010525"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p17432141014217"><a name="p17432141014217"></a><a name="p17432141014217"></a>project</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p1443261017218"><a name="p1443261017218"></a><a name="p1443261017218"></a>项目名称，需要与服务端对应配置文件中的project匹配</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p2432010828"><a name="p2432010828"></a><a name="p2432010828"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p143215103213"><a name="p143215103213"></a><a name="p143215103213"></a>-</p>
</td>
</tr>
<tr id="row104321010525"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p17432141014217"><a name="p17432141014217"></a><a name="p17432141014217"></a>engine</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p1443261017218"><a name="p1443261017218"></a><a name="p1443261017218"></a>调优算法</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p2432010828"><a name="p2432010828"></a><a name="p2432010828"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p143215103213"><a name="p143215103213"></a><a name="p143215103213"></a>"random", "forest", "gbrt", "bayes", "extraTrees"</p>
</td>
</tr>
<tr id="row16432310326"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p17432191018213"><a name="p17432191018213"></a><a name="p17432191018213"></a>iterations</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p243217101521"><a name="p243217101521"></a><a name="p243217101521"></a>调优迭代次数</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p543211018210"><a name="p543211018210"></a><a name="p543211018210"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p1343231017218"><a name="p1343231017218"></a><a name="p1343231017218"></a>&gt;=10</p>
</td>
</tr>
<tr id="row1543215101726"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p2043215101522"><a name="p2043215101522"></a><a name="p2043215101522"></a>random_starts</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p9432210228"><a name="p9432210228"></a><a name="p9432210228"></a>随机迭代次数</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p1543214101927"><a name="p1543214101927"></a><a name="p1543214101927"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p443214107215"><a name="p443214107215"></a><a name="p443214107215"></a>&lt;iterations</p>
</td>
</tr>
<tr id="row1543215101726"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p2043215101522"><a name="p2043215101522"></a><a name="p2043215101522"></a>feature_filter_engine</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p9432210228"><a name="p9432210228"></a><a name="p9432210228"></a>参数搜索算法，用于重要参数选择，该参数可选</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p1543214101927"><a name="p1543214101927"></a><a name="p1543214101927"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p443214107215"><a name="p443214107215"></a><a name="p443214107215"></a>"lhs"</p>
</td>
</tr>
<tr id="row1543215101726"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p2043215101522"><a name="p2043215101522"></a><a name="p2043215101522"></a>feature_filter_cycle</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p9432210228"><a name="p9432210228"></a><a name="p9432210228"></a>参数搜索轮数，用于重要参数选择，该参数配合feature_filter_engine使用</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p1543214101927"><a name="p1543214101927"></a><a name="p1543214101927"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p443214107215"><a name="p443214107215"></a><a name="p443214107215"></a>-</p>
</td>
</tr>
<tr id="row1543215101726"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p2043215101522"><a name="p2043215101522"></a><a name="p2043215101522"></a>feature_filter_iters</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p9432210228"><a name="p9432210228"></a><a name="p9432210228"></a>每轮参数搜索的迭代次数，用于重要参数选择，该参数配合feature_filter_engine使用</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p1543214101927"><a name="p1543214101927"></a><a name="p1543214101927"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p443214107215"><a name="p443214107215"></a><a name="p443214107215"></a>-</p>
</td>
</tr>
<tr id="row1543215101726"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p2043215101522"><a name="p2043215101522"></a><a name="p2043215101522"></a>split_count</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p9432210228"><a name="p9432210228"></a><a name="p9432210228"></a>调优参数取值范围中均匀选取的参数个数，用于重要参数选择，该参数配合feature_filter_engine使用</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p1543214101927"><a name="p1543214101927"></a><a name="p1543214101927"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p443214107215"><a name="p443214107215"></a><a name="p443214107215"></a>-</p>
</td>
</tr>
<tr id="row1543215101726"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p2043215101522"><a name="p2043215101522"></a><a name="p2043215101522"></a>benchmark</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p9432210228"><a name="p9432210228"></a><a name="p9432210228"></a>性能测试脚本</p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p1543214101927"><a name="p1543214101927"></a><a name="p1543214101927"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p443214107215"><a name="p443214107215"></a><a name="p443214107215"></a>-</p>
</td>
</tr>
<tr id="row84323102029"><td class="cellrowborder" valign="top" width="16.84%" headers="mcps1.2.5.1.1 "><p id="p18432111012218"><a name="p18432111012218"></a><a name="p18432111012218"></a>evaluations</p>
</td>
<td class="cellrowborder" valign="top" width="19.97%" headers="mcps1.2.5.1.2 "><p id="p6432121016218"><a name="p6432121016218"></a><a name="p6432121016218"></a>性能测试评估指标</p>
<p id="p1613443674418"><a name="p1613443674418"></a><a name="p1613443674418"></a>evaluations 配置项请参见<a href="#table58847714266">表4</a></p>
</td>
<td class="cellrowborder" valign="top" width="15.72%" headers="mcps1.2.5.1.3 "><p id="p124321710422"><a name="p124321710422"></a><a name="p124321710422"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.47%" headers="mcps1.2.5.1.4 "><p id="p743214101326"><a name="p743214101326"></a><a name="p743214101326"></a>-</p>
</td>
</tr>
</tbody>
</table>

**表 4**  evaluations项配置说明

<a name="table58847714266"></a>

<table><thead align="left"><tr id="row96719161245"><th class="cellrowborder" valign="top" width="12.950000000000001%" id="mcps1.2.5.1.1"><p id="p49973411241"><a name="p49973411241"></a><a name="p49973411241"></a><strong id="b1999714118410"><a name="b1999714118410"></a><a name="b1999714118410"></a>配置名称</strong></p>
</th>
<th class="cellrowborder" valign="top" width="24.23%" id="mcps1.2.5.1.2"><p id="p119971941941"><a name="p119971941941"></a><a name="p119971941941"></a><strong id="b11997114111414"><a name="b11997114111414"></a><a name="b11997114111414"></a>配置说明</strong></p>
</th>
<th class="cellrowborder" valign="top" width="15.629999999999999%" id="mcps1.2.5.1.3"><p id="p1899784117416"><a name="p1899784117416"></a><a name="p1899784117416"></a><strong id="b29983411244"><a name="b29983411244"></a><a name="b29983411244"></a>参数类型</strong></p>
</th>
<th class="cellrowborder" valign="top" width="47.19%" id="mcps1.2.5.1.4"><p id="p1099814112416"><a name="p1099814112416"></a><a name="p1099814112416"></a><strong id="b19981411445"><a name="b19981411445"></a><a name="b19981411445"></a>取值范围</strong></p>
</th>
</tr>
</thead>
<tbody><tr id="row159636710262"><td class="cellrowborder" valign="top" width="12.950000000000001%" headers="mcps1.2.5.1.1 "><p id="p9963679262"><a name="p9963679262"></a><a name="p9963679262"></a>name</p>
</td>
<td class="cellrowborder" valign="top" width="24.23%" headers="mcps1.2.5.1.2 "><p id="p10963378267"><a name="p10963378267"></a><a name="p10963378267"></a>评价指标名称</p>
</td>
<td class="cellrowborder" valign="top" width="15.629999999999999%" headers="mcps1.2.5.1.3 "><p id="p86031433840"><a name="p86031433840"></a><a name="p86031433840"></a>字符串</p>
</td>
<td class="cellrowborder" valign="top" width="47.19%" headers="mcps1.2.5.1.4 "><p id="p247112292045"><a name="p247112292045"></a><a name="p247112292045"></a>-</p>
</td>
</tr>
<tr id="row496313714269"><td class="cellrowborder" valign="top" width="12.950000000000001%" headers="mcps1.2.5.1.1 "><p id="p696313782618"><a name="p696313782618"></a><a name="p696313782618"></a>get</p>
</td>
<td class="cellrowborder" valign="top" width="24.23%" headers="mcps1.2.5.1.2 "><p id="p16963147102617"><a name="p16963147102617"></a><a name="p16963147102617"></a>获取性能评估结果的脚本</p>
</td>
<td class="cellrowborder" valign="top" width="15.629999999999999%" headers="mcps1.2.5.1.3 "><p id="p360310338414"><a name="p360310338414"></a><a name="p360310338414"></a>-</p>
</td>
<td class="cellrowborder" valign="top" width="47.19%" headers="mcps1.2.5.1.4 "><p id="p204715298417"><a name="p204715298417"></a><a name="p204715298417"></a>-</p>
</td>
</tr>
<tr id="row5963107142620"><td class="cellrowborder" valign="top" width="12.950000000000001%" headers="mcps1.2.5.1.1 "><p id="p169631073264"><a name="p169631073264"></a><a name="p169631073264"></a>type</p>
</td>
<td class="cellrowborder" valign="top" width="24.23%" headers="mcps1.2.5.1.2 "><p id="p29631478264"><a name="p29631478264"></a><a name="p29631478264"></a>评估结果的正负类型，positive代表最小化性能值，negative代表最大化对应性能值</p>
</td>
<td class="cellrowborder" valign="top" width="15.629999999999999%" headers="mcps1.2.5.1.3 "><p id="p76031331415"><a name="p76031331415"></a><a name="p76031331415"></a>枚举</p>
</td>
<td class="cellrowborder" valign="top" width="47.19%" headers="mcps1.2.5.1.4 "><p id="p1647116291411"><a name="p1647116291411"></a><a name="p1647116291411"></a>"positive","negative"</p>
</td>
</tr>
<tr id="row59635792614"><td class="cellrowborder" valign="top" width="12.950000000000001%" headers="mcps1.2.5.1.1 "><p id="p096320712268"><a name="p096320712268"></a><a name="p096320712268"></a>weight</p>
</td>
<td class="cellrowborder" valign="top" width="24.23%" headers="mcps1.2.5.1.2 "><p id="p2096347192620"><a name="p2096347192620"></a><a name="p2096347192620"></a>该指标的权重百分比，0-100</p>
</td>
<td class="cellrowborder" valign="top" width="15.629999999999999%" headers="mcps1.2.5.1.3 "><p id="p1666738163"><a name="p1666738163"></a><a name="p1666738163"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.19%" headers="mcps1.2.5.1.4 "><p id="p154712292047"><a name="p154712292047"></a><a name="p154712292047"></a>0-100</p>
</td>
</tr>
<tr id="row17963117152615"><td class="cellrowborder" valign="top" width="12.950000000000001%" headers="mcps1.2.5.1.1 "><p id="p6963677267"><a name="p6963677267"></a><a name="p6963677267"></a>threshold</p>
</td>
<td class="cellrowborder" valign="top" width="24.23%" headers="mcps1.2.5.1.2 "><p id="p19632712261"><a name="p19632712261"></a><a name="p19632712261"></a>该指标的最低性能要求</p>
</td>
<td class="cellrowborder" valign="top" width="15.629999999999999%" headers="mcps1.2.5.1.3 "><p id="p36031331245"><a name="p36031331245"></a><a name="p36031331245"></a>整型</p>
</td>
<td class="cellrowborder" valign="top" width="47.19%" headers="mcps1.2.5.1.4 "><p id="p447132914413"><a name="p447132914413"></a><a name="p447132914413"></a>用户指定</p>
</td>
</tr>
</tbody>
</table>

### 配置示例

服务端yaml文件配置示例：

```Conf
project: "compress"
maxiterations: 500
startworkload: ""
stopworkload: ""
object :
  -
    name : "compressLevel"
    info :
        desc : "The compresslevel parameter is an integer from 1 to 9 controlling the level of compression"
        get : "cat /root/A-Tune/examples/tuning/compress/compress.py | grep 'compressLevel=' | awk -F '=' '{print $2}'"
        set : "sed -i 's/compressLevel=\\s*[0-9]*/compressLevel=$value/g' /root/A-Tune/examples/tuning/compress/compress.py"
        needrestart : "false"
        type : "continuous"
        scope :
          - 1
          - 9
        dtype : "int"
  -
    name : "compressMethod"
    info :
        desc : "The compressMethod parameter is a string controlling the compression method"
        get : "cat /root/A-Tune/examples/tuning/compress/compress.py | grep 'compressMethod=' | awk -F '=' '{print $2}' | sed 's/\"//g'"
        set : "sed -i 's/compressMethod=\\s*[0-9,a-z,\"]*/compressMethod=\"$value\"/g' /root/A-Tune/examples/tuning/compress/compress.py"
        needrestart : "false"
        type : "discrete"
        options :
          - "bz2"
          - "zlib"
          - "gzip"
        dtype : "string"
```

客户端yaml文件配置示例：

```yaml
project: "compress"
engine : "gbrt"
iterations : 20
random_starts : 10

benchmark : "python3 /root/A-Tune/examples/tuning/compress/compress.py"
evaluations :
  -
    name: "time"
    info:
        get: "echo '$out' | grep 'time' | awk '{print $3}'"
        type: "positive"
        weight: 20
  -
    name: "compress_ratio"
    info:
        get: "echo '$out' | grep 'compress_ratio' | awk '{print $3}'"
        type: "negative"
        weight: 80
```

### 使用示例

- 下载测试数据

    ```sh
    wget http://cs.fit.edu/~mmahoney/compression/enwik8.zip
    ```

- 准备调优环境
    prepare.sh文件示例：

    ```sh
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
    ```

    运行脚本：

    ```sh
    sh prepare.sh enwik8.zip
    ```

- 进行tuning调优

    ```sh
    atune-adm tuning --project compress --detail compress_client.yaml
    ```

- 恢复tuning调优前的初始配置，compress为yaml文件中的项目名称

    ```sh
    atune-adm tuning --restore --project compress
    ```
