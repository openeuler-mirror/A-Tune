## 安装flink

注：nexmark当前支持的最新flink版本是 1.13.0

参考：https://nightlies.apache.org/flink/flink-docs-release-1.13/docs/deployment/resource-providers/standalone/overview/

### 环境准备

```bash
# install jdk
yum install java java-devel
echo "export JAVA_HOME=$(ls -d /usr/lib/jvm/java)" >> /etc/profile
echo 'export PATH=$PATH:$JAVA_HOME/bin' >> /etc/profile

# install maven
wget https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.5/apache-maven-3.9.5-bin.tar.gz
tar zxf apache-maven-3.9.5-bin.tar.gz -C /opt
echo 'export PATH=$PATH:/opt/apache-maven-3.9.5/bin' >> /etc/profile

# install flink
wget https://archive.apache.org/dist/flink/flink-1.13.0/flink-1.13.0-bin-scala_2.12.tgz
tar -xf flink-1.13.0-bin-scala_2.12.tgz -C /opt
ln -s /opt/flink-1.13.0 /optflink
echo 'export FLINK_HOME=/opt/flink' >> /etc/profile
echo 'export PATH=$PATH:$FLINK_HOME/bin' >> /etc/profile
source /etc/profile
```

### 启动flink

```bash
cd /opt/flink
./bin/start-cluster.sh
```

相关进程：

```
jps
```

TaskManagerRunner
StandaloneSessionClusterEntrypoint

日志：

```
ll ./log/flink-root-standalonesession-*.log
```

### 停止flink

```bash
./bin/stop-cluster.sh
```

### 验证flink：提交作业（Job）

Flink 提供了一个 CLI 工具 bin/flink，它可以运行打包为 Java ARchives (JAR) 的程序，并控制其执行。 

Flink 的 Releases 附带了许多的示例作业。您可以在 examples/ 文件夹中找到。

要将字数统计作业示例部署到运行中的群集，请执行以下命令：

```bash
./bin/flink run examples/streaming/WordCount.jar
```

您可以通过查看日志来验证输出结果：

```bash
tail log/flink-*-taskexecutor-*.out
```

输出示例：

```bash
  (nymph,1)
  (in,3)
  (thy,1)
  (orisons,1)
  (be,4)
  (all,2)
  (my,1)
  (sins,1)
  (remember,1)
  (d,4)
```

## 安装nexmark

参考：https://github.com/nexmark/nexmark

### 配置环境变量

```
# 选择java 11以上
yum install java java-devel
```

### 配置maven代理

注：不需要则不配置。需替换 PROXY 相关变量为实际配置值。
```bash
#修改/opt/apache-maven-3.9.5/conf/settings.xml
  <proxies>
    <proxy>
      <id>myproxy</id>
      <active>true</active>
      <protocol>http</protocol>
      <host>{PROXY_URL}</host>
      <port>{PROXY_PORT}</port>
      <username>{PROXY_USER}</username>
      <password>{PROXY_PASSWD}</password>
    </proxy>
  </proxies>
```

### 构建安装nexmark

```bash
cd /opt
wget https://github.com/nexmark/nexmark/archive/refs/tags/v0.2.0.tar.gz -O nexmark-0.2.0.tar.gz
cd nexmark-0.2.0/nexmark-flink
./build.sh
# build.sh输出日志
#[INFO] Scanning for projects...
#[INFO] 
#[INFO] ------------------< com.github.nexmark:nexmark-flink >------------------
#[INFO] Building nexmark-flink 0.3-SNAPSHOT
#[INFO]   from pom.xml
#[INFO] --------------------------------[ jar ]---------------------------------
#Downloading from central: https://repo.maven.apache.org/maven2/org/apache/maven/plugins/maven-shad
#Downloaded from central: https://repo.maven.apache.org/maven2/org/apache/maven/plugins/maven-shade
# ...
#[INFO] --- assembly:3.6.0:single (bin) @ nexmark-flink ---
#[INFO] Reading assembly descriptor: src/main/assemblies/bin.xml
#[INFO] Copying files to /opt/nexmark-0.2.0/nexmark-flink/target/nexmark-flink-bin
#[WARNING] Assembly file: /opt/nexmark-0.2.0/nexmark-flink/target/nexmark-flink-bin is not a reguloyment.
#[INFO] ------------------------------------------------------------------------
#[INFO] BUILD SUCCESS
#[INFO] ------------------------------------------------------------------------
#[INFO] Total time:  24:15 min
#[INFO] Finished at: 2025-11-14T18:36:58+08:00
#[INFO] ------------------------------------------------------------------------
# 当前目录生成 nexmark-flink.tgz
tar xzf nexmark-flink.tgz -C /opt
cd /opt/
ln -s nexmark-flink nexmark
# 拷贝jar到flink库目录
cp /opt/nexmark/lib/*.jar /opt/flink/lib
```

### 配置nexmark&Flink

编辑 Nexmark 配置文件 nexmark-flink/conf/flink-conf.yaml：

```powershell
# 基本配置 (无需修改)
taskmanager.memory.process.size: 8G
jobmanager.rpc.address: localhost
jobmanager.rpc.port: 6123
jobmanager.memory.process.size: 8G
taskmanager.numberOfTaskSlots: 1
parallelism.default: 8
io.tmp.dirs: /tmp

# JVM options for GC (取消GC打印)
#env.java.opts: -verbose:gc -XX:NewRatio=3 -XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:ParallelGCThreads=4
#env.java.opts.jobmanager: -Xloggc:$FLINK_LOG_DIR/jobmanager-gc.log -XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=2 -XX:GCLogFileSize=512M
#env.java.opts.taskmanager: -Xloggc:$FLINK_LOG_DIR/taskmanager-gc.log -XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=2 -XX:GCLogFileSize=512M
env.java.opts: -XX:ParallelGCThreads=4

# State & Checkpoint (配置目录)
state.checkpoints.dir: file:///opt/checkpoint
state.backend.rocksdb.localdir: /tmp
```

准备目录，拷贝配置文件到flink目录：

```
cp nexmark/conf/flink-conf.yaml flink/conf/
mkdir -p /opt/checkpoint
```

nexmark配置文件：(无需修改)

```bash
nexmark.workload.suite.100m.events.num: 100000000
nexmark.workload.suite.100m.tps: 10000000
nexmark.workload.suite.100m.queries: "q0,q1,q2,q3,q4,q5,q7,q8,q9,q10,q11,q12,q13,q14,q15,q16,q17,q18,q19,q20,q21,q22"
```

## 运行benchmark
### 启动Flink&benchmark cluster

```bash
# 清理
nexmark/bin/shutdown_cluster.sh
flink/bin/stop-cluster.sh
rm -f nexmark/log/*
rm -f flink/log/*
# 运行
flink/bin/start-cluster.sh
nexmark/bin/setup_cluster.sh
```

### 运行Nexmark

-   运行所有query

```
nexmark/bin/run_query.sh all
```

It will run all the queries one by one, and collect benchmark metrics automatically. It will take 50 minutes to finish the benchmark by default. 
At last, it will print the benchmark summary result (Cores * Time(s) for each query) on the console.

-   仅运行q0压测（推荐）

```
nexmark/bin/run_query.sh q0
```

-   压测屏幕输出

```bash
(venv) [root@syn-076-053-246-109 opt]# nexmark/bin/run_query.sh q0
Benchmark Queries: [q0]
==================================================================
Start to run query q0 with workload [tps=10 M, eventsNum=100 M, percentage=bid:46,auction:3,person:1,kafkaServers:null]
Monitor metrics after 10 seconds.
Start to monitor metrics until job is finished.
Current Cores=1.03 (1 TMs)
Current Cores=1.03 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.05 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.18 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.19 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.02 (1 TMs)
Current Cores=1.01 (1 TMs)
Current Cores=1.03 (1 TMs)
Summary Average: EventsNum=100,000,000, Cores=1.03, Time=209.147 s
Stop job query q0
-------------------------------- Nexmark Results --------------------------------

+-------------------+-------------------+-------------------+-------------------+-------------------+-------------------+
| Nexmark Query     | Events Num        | Cores             | Time(s)           | Cores * Time(s)   | Throughput/Cores  |
+-------------------+-------------------+-------------------+-------------------+-------------------+-------------------+
|q0                 |100,000,000        |1.03               |209.147            |214.492            |466.22 K/s         |
|Total              |100,000,000        |1.026              |209.147            |214.492            |466.22 K/s         |
+-------------------+-------------------+-------------------+-------------------+-------------------+-------------------+


```



## 定位相关手段

### flink日志

-   SESSION日志：log/flink-root-standalonesession-0-localhost.log（每次新启动，增加后缀.XX）

    ```bash
    2025-11-18 09:31:33,712 INFO  org.apache.flink.runtime.dispatcher.DispatcherRestEndpoint   [] - Starting rest endpoint.
    2025-11-18 09:31:33,997 INFO  org.apache.flink.runtime.webmonitor.WebMonitorUtils          [] - Determined location of main cluster component log file: /opt/flink-1.13.0/log/flink-root-standalonesession-0-localhost.log
    2025-11-18 09:31:33,997 INFO  org.apache.flink.runtime.webmonitor.WebMonitorUtils          [] - Determined location of main cluster component stdout file: /opt/flink-1.13.0/log/flink-root-standalonesession-0-localhost.out
    2025-11-18 09:31:34,205 INFO  org.apache.flink.runtime.dispatcher.DispatcherRestEndpoint   [] - Rest endpoint listening at localhost:8081
    2025-11-18 09:31:34,207 INFO  org.apache.flink.runtime.dispatcher.DispatcherRestEndpoint   [] - http://localhost:8081 was granted leadership with leaderSessionID=00000000-0000-0000-0000-000000000000
    2025-11-18 09:31:34,208 INFO  org.apache.flink.runtime.dispatcher.DispatcherRestEndpoint   [] - Web frontend listening at http://localhost:8081.
    ```

-   EXECUTOR日志：log/flink-root-taskexecutor-0-localhost.log（每次新启动，增加后缀.XX）

    ```bash
    --------------------------------------------------------------------------------
    2025-11-18 00:44:55,677 INFO  org.apache.flink.runtime.taskexecutor.TaskManagerRunner      [] -  Starting TaskManager (Version: 1.13.0, Scala: 2.12, Rev:f06faf1, Date:2021-04-23T15:39:21+02:00)
    2025-11-18 00:44:55,677 INFO  org.apache.flink.runtime.taskexecutor.TaskManagerRunner      [] -  OS current user: root
    2025-11-18 00:44:55,677 INFO  org.apache.flink.runtime.taskexecutor.TaskManagerRunner      [] -  Current Hadoop/Kerberos user: <no hadoop dependency found>
    2025-11-18 00:44:55,677 INFO  org.apache.flink.runtime.taskexecutor.TaskManagerRunner      [] -  JVM: OpenJDK 64-Bit Server VM - BiSheng - 11/11.0.27+6
    2025-11-18 00:44:55,677 INFO  org.apache.flink.runtime.taskexecutor.TaskManagerRunner      [] -  Maximum heap size: 3432 MiBytes
    2025-11-18 00:44:55,678 INFO  org.apache.flink.runtime.taskexecutor.TaskManagerRunner      [] -  JAVA_HOME: /usr/lib/jvm/java
    2025-11-18 00:44:55,678 INFO  org.apache.flink.runtime.taskexecutor.TaskManagerRunner      [] -  No Hadoop Dependency available
    ```

### nexmark日志

-   压测日志：/opt/nexmark/log/nexmark-flink.log

```bash
==================================================================
2025-11-18 09:31:42,689 INFO  com.github.nexmark.flink.QueryRunner                         [] - Start to run query q0 with workload [tps=10 M, eventsNum=100 M, percentage=bid:46,auction:3,person:1,kafkaServers:null]
2025-11-18 09:31:42,696 INFO  com.github.nexmark.flink.QueryRunner                         [] - 
================================================================================
Query q0 is running.
--------------------------------------------------------------------------------

2025-11-18 09:31:43,088 INFO  com.github.nexmark.flink.metric.cpu.CpuMetricReceiver        [] - Received CPU metric report: [{"host":"127.0.0.1","pid":1501895,"cpu":-0.01}]

2025-11-18 09:31:46,224 INFO  com.github.nexmark.flink.QueryRunner                         [] - Flink SQL> [34;1m[INFO] Submitting SQL update statement to the cluster...[0m
2025-11-18 09:31:47,888 INFO  com.github.nexmark.flink.metric.cpu.CpuMetricReceiver        [] - Received CPU metric report: [{"host":"127.0.0.1","pid":1501895,"cpu":0.02204408884048462}]
2025-11-18 09:31:52,663 INFO  com.github.nexmark.flink.QueryRunner                         [] - [34;1m[INFO] SQL update statement has been successfully submitted to the cluster:[0m
2025-11-18 09:31:52,663 INFO  com.github.nexmark.flink.QueryRunner                         [] - Job ID: 9017d011306bb8cca50b7186584f470e
2025-11-18 09:31:52,665 INFO  com.github.nexmark.flink.QueryRunner                         [] - Flink SQL> 
2025-11-18 09:31:52,666 INFO  com.github.nexmark.flink.QueryRunner                         [] - Shutting down the session...
2025-11-18 09:31:52,666 INFO  com.github.nexmark.flink.QueryRunner                         [] - done.

2025-11-18 09:32:02,875 INFO  com.github.nexmark.flink.metric.cpu.CpuMetricReceiver        [] - Received CPU metric report: [{"host":"127.0.0.1","pid":1501895,"cpu":1.0445376586914064}]
2025-11-18 09:32:02,876 INFO  com.github.nexmark.flink.metric.MetricReporter               [] - Current Cores=1.04 (1 TMs)
2025-11-18 09:32:07,867 INFO  com.github.nexmark.flink.metric.cpu.CpuMetricReceiver        [] - Received CPU metric report: [{"host":"127.0.0.1","pid":1501895,"cpu":1.0196314239501953}]
2025-11-18 09:32:07,886 INFO  com.github.nexmark.flink.metric.MetricReporter               [] - Current Cores=1.02 (1 TMs)
2025-11-18 09:32:12,867 INFO  com.github.nexmark.flink.metric.cpu.CpuMetricReceiver        [] - Received CPU metric report: [{"host":"127.0.0.1","pid":1501895,"cpu":1.011797637939453}]
2025-11-18 09:32:12,892 INFO  com.github.nexmark.flink.metric.MetricReporter               [] - Current Cores=1.01 (1 TMs)

2025-11-18 09:36:34,376 INFO  com.github.nexmark.flink.metric.MetricReporter               [] - Summary Average: EventsNum=100,000,000, Cores=1.03, Time=281.607 s
2025-11-18 09:36:34,376 INFO  com.github.nexmark.flink.QueryRunner                         [] - Stop job query q0
```

-   指标日志：

    ```bash
    2025-11-18 09:31:37,847 INFO  com.github.nexmark.flink.metric.cpu.CpuMetricSender          [] - Start to monitor process: [1501895]
    
    2025-11-18 09:36:22,861 INFO  com.github.nexmark.flink.metric.cpu.CpuMetricSender          [] - Report CPU metric: [{"host":"127.0.0.1","pid":1501895,"cpu":1.008000030517578}]
    2025-11-18 09:36:27,861 INFO  com.github.nexmark.flink.metric.cpu.CpuMetricSender          [] - Report CPU metric: [{"host":"127.0.0.1","pid":1501895,"cpu":1.015999984741211}]
    2025-11-18 09:36:32,861 INFO  com.github.nexmark.flink.metric.cpu.CpuMetricSender          [] - Report CPU metric: [{"host":"127.0.0.1","pid":1501895,"cpu":1.01}]
    ```

### FLINK Restful API查询

参考：https://nightlies.apache.org/flink/flink-docs-master/docs/ops/rest_api/

```bash
# 基础信息
# 1. 集群概览:
curl -s http://localhost:8081/overview | jq .

# 2. 当前作业列表:
curl -s http://localhost:8081/jobs | jq .

# 3. TaskManager 状态:
curl -s http://localhost:8081/taskmanagers | jq '.taskmanagers[] | {id: .id, slots: .slotsAvailable, total: .slotsTotal}'

# 4. 如果有运行中的作业，显示详细信息
JOB_ID=$(curl -s http://localhost:8081/jobs | jq -r '.jobs[] | select(.status=="RUNNING") | .id' | head -1)
if [ ! -z "$JOB_ID" ]; then
    # 运行中作业详情 (ID: $JOB_ID)，状态、顶点、背压:
    curl -s http://localhost:8081/jobs/$JOB_ID | jq '.state'
    curl -s http://localhost:8081/jobs/$JOB_ID/vertices | jq '.vertices[] | {name: .name, parallelism: .parallelism, status: .status}'
    curl -s http://localhost:8081/jobs/$JOB_ID/backpressure | jq .
fi
```

# 部署 copilot
* 详细安装方法参见[EulerCopilot Tune 安装使用指南](../../README.md)

## 1. 下载 copilot 源码
```bash
git clone https://gitee.com/openeuler/A-Tune.git
cd A-Tune/
# 切换到 euler-copilot-tune 分支
git checkout euler-copilot-tune
```
## 2. 安装系统依赖
```bash
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
## 3. 修改配置文件
*  __环境信息 config/.env.yaml 配置__
```YAML
# LLM 服务配置示例
# 根据实际使用的模型服务（如 OpenAI、通义千问、deepseek 等）填写以下字段
LLM_KEY: "sk-XXXXXX"                    # 必填：模型服务的 API 密钥
LLM_URL: "https://api.deepseek.com"     # 必填：LLM 服务的 API 接口地址，如 "https://api.deepseek.com"
LLM_MODEL_NAME: "deepseek-chat"         # 必填：要调用的模型名，如 deepseek-chat
LLM_MAX_TOKENS:                         # 选填：生成文本的最大 token 数，如512或2048

# 部署应用的机器 ip 信息（重点补充 ip、host_user、password）
servers:
  - ip: ""                              #应用所在ip
    host_user: ""                       #登录机器的usr id
    password: ""                        #登录机器的密码
    port: 22                            #应用所在ip的具体port
    app: "flink"                        #调优应用的name
    target_process_name: "flink"
    business_context: "高并发流处理服务"
    max_retries: 3
    delay: 1.0
```
* __应用部署信息 config/app_config.yaml 配置__        
需按实际环境填写；一般无需修改，若部署方式不同需要修改对应命令。
```YAML
flink:
  config_file: "/opt/flink/conf/flink-conf.yaml"
  set_param_template: 'grep -q "^\\s*$param_name\\s\\+" "$config_file" && sed -i "s/^\\s*$param_name\\s\\+.*/$param_name $param_value/g" $config_file || echo "$param_name $param_value" >> "$config_file"'
  get_param_template: 'grep -oP "^\s*$param_name\s*\K.*" "$config_file"'
  benchmark: "sh $SCRIPTS_DIR/flink/parse_benchmark.sh"
  stop_workload: 'source /etc/profile && /opt/flink/bin/stop-cluster.sh && /opt/nexmark/bin/shutdown_cluster.sh'
  start_workload: 'source /etc/profile && /opt/flink/bin/start-cluster.sh && /opt/nexmark/bin/setup_cluster.sh'
  performance_metric: "THROUGHPUT"
```

* __scripts/flink/parse_benchmark.sh 脚本内容：__
```YAML
LOG_FILE=/home/benchmark.log

echo 1 > /tmp/euler-copilot-fifo
source /etc/profile > /dev/null 2>&1
/opt/flink/bin/stop-cluster.sh > /dev/null 2>&1
/opt/nexmark/bin/shutdown_cluster.sh > /dev/null 2>&1
/opt/flink/bin/start-cluster.sh > /dev/null 2>&1
/opt/nexmark/bin/setup_cluster.sh > /dev/null 2>&1

/opt/nexmark/bin/run_query.sh q0  > $LOG_FILE 2>&1

total_throughput=$(grep '|Total' "$LOG_FILE" | awk -F'|' '
  {
    # ~O~V~@~R~U__~L~H~W~L~N__|
    gsub(/^ +| +$/, "", $(NF-1))
    split($(NF-1), a, " ")
    val = a[1]
    unit = a[2]
    if (unit == "M/s") val *= 1000
    total += val
  }
  END {printf "%.3f\n", total}
')

echo "$total_throughput"

```

## 4. 执行调优程序
```bash
# 在源码根目录执行
export PYTHONPATH="`pwd`:$PYTHONPATH"
python3 src/start_tune.py
```