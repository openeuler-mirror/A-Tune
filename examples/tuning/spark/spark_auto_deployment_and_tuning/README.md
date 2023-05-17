## Spark 自动化部署和HiBench基准性能测试

### **工作流程**

一、**Spark 自动化部署流程**

1. 安装 gcc make curl wget samba git
2. 关闭防火墙并启动nmbd.service
3. 配置本机免密登录
4. 安装Java和配置Java 环境
5. 安装Hadoop并配置Hadoop环境，格式化namenode并启动hdfs和yarn
7. 安装Spark并配置Spark环境，启动Spark master和worker守护进程

二、**HiBench 自动化部署流程**

1. 安装python2
2. 安装Maven并配置Maven环境变量和设置maven仓库国内镜像
3. 为Spark Benchmark下载并编译、配置HiBench

三、**执行 Benchmark**

1. 准备工作
2. 执行测试

## 开始操作

**前提条件**

- 将本目录及所有文件和子目录放到您的主机所在的目录，用`ip addr`查看本机ip，`hostname`命令查看本机名称，然后在`/etc/hosts`中添加`ip hostname`，例如：`192.168.70.129 spark`

- 关闭防火墙:

  ```bash
  systemctl stop firewalld
  ```

- 执行系统更新，并安装必要依赖

  ```bash
  dnf update -y
  dnf install gcc make curl wget samba git atune atune-engine -y
  ```

- 启动服务：

  ```bash
  systemctl start nmb
  systemctl start atuned
  systemctl start atune-engine
  ```

  **PS**: atuned和atune-engine可能启动不成功，需要将`/etc/atuned/atuned.cnf`中的`rest_tls`和`engine_tls`置为false，并把`network`置为自己的网络；`/etc/atuned/engine.cnf`中的`engine_tls`置为false。

- 配置免密登录

  ```bash
  ssh-keygen -t rsa
  cat ~/.ssh/id_rsa.pub >>~/.ssh/authorized_keys
  ```

  

在自动化部署的过程中，需要下载大量的文件，如果遇到网络问题导致安装不成功，可以配置代理：

```bash
# 为git配置代理执行：
git config --global http.proxy http://ip:port
git config --global https.proxy http://ip:port

# 为系统设置代理，可以在~/.bashrc中添加如下：
export http_proxy=http://ip:port
export https_proxy=http://ip:port
# 使环境变量立即生效
source ~/.bashrc

#注意上面的ip和port替换为自己的代理地址
```

### **Spark 自动化部署**

切换到脚本所在的目录，执行`chmod u+x ./install_spark.sh`，为脚本添加执行权限，然后执行脚本`./install_spark.sh`，期间可能需要输入管理员密码，等待片刻终端出现`Spark deployment success.`的字样，代表执行成功，执行`source ~/.bashrc`和`jps`命令，查看正在运行的守护进程为:`NameNode、NodeManager、SecondaryNameNode、ResourceManager、DataNode、Master、Worker`

如果运行不成功，可以查看本目录的install_spark.log日志文件，可以看到哪一步未成功。

### HiBench 自动化部署

切换到脚本所在的目录，执行`chmod u+x ./install_hibench.sh`，为脚本添加执行权限，然后执行脚本`./install_hibench.sh`，期间可能需要输入管理员密码，等待片刻终端出现`Hibench init success`的字样，代表执行成功。

如果运行不成功，可以查看本目录的install_hibench.log日志文件，可以看到哪一步未成功。

### 执行基本Benchmark

切换到脚本所在的目录：

```bash
sh HiBench/bin/workloads/sql/join/prepare/prepare.sh
sh HiBench/bin/workloads/sql/join/spark/run.sh
# 结果
cat HiBench/report/hibench.log
```

## A-tune HiBench性能调优

**实例机器具体参数**

- 虚拟化：Vmware Workstation 17
- 操作系统：Openeuler 22.03 SP1
- CPU：AMD Ryzen 7 4800H with Radeon Graphics (虚拟机 2CPU 4Core)
- Memery：8G
- Disk：128G

**Spark调优参数：**

- num_executors：执行器数量 （2~4）
- executor_core：每个执行器核心数 （2~4）
- executor_memory：执行器内存 （1g~4g）
- driver_memory：driver内存 （1g-2g）
- default_parallelism：默认并行度 （10~50）
- storageLevel：rdd默认存储级别(0~2)
- shuffle_partition：shuffle分区个数(1~4)

**HDFS数据规模调整为huge(参见HiBench调整测试数据规模)**

### 开始测试

首先，生成测试数据：`sh HiBench/bin/workloads/sql/join/prepare/prepare.sh`

将`spark_hibench_server.yaml`拷贝到`/etc/atuned/tuning`下：

```bash
cp spark_hibench_server.yaml /etc/atuned/tuning
# 注意要修改spark_hibench_server.yaml 中设置的所有get和set的路径应该指向spark_hibench.sh的所在位置
```

开始执行性能调优：

```bash
atune-adm tuning --project spark_hibench --detail ./spark_hibench_client.yaml
```



**Notice：实例测试结果保存在本目录下atune_spark_bench.log文件**
