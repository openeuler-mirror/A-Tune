# EulerCopilot Tune 安装与使用指南

## 项目简介
EulerCopilot Tune 通过采集系统、微架构、应用等维度的指标数据，结合大语言模型与定制化 Prompt 工程，针对不同应用的可调参数给出可靠的参数推荐。同时，根据推荐的参数运行 benchmark 并与 baseline 进行对比，可以计算出推荐参数对应用性能的提升值。

当前已基于云大数存四大场景的多种应用场景完成验证（环境规格为8u32g oe2403sp2）：
- mysql：QPS提升22.37%，验证场景sysbench（10张table表，每张表10000行数据，并发线程数128，随机数模式uniform，oltp_read_wrtie读写混合负载模式）
- pgsql：QPS提升211.45%，验证场景sysbench（10张table表，每张表100000行数据，并发线程数32，随机数模式uniform，oltp_read_wrtie读写混合负载模式）
- redis：QPS提升8.80%，验证场景redis-benchmark（单机部署应用，无持久化负载，测试过程中动态生成key-value数据，键值均为随机值，测试命令集set/get/incr/rpop/sadd/hset/lrange_600）
- spark：time_taken(SQL执行耗时)降低27.46%，验证场景spark-sql（单节点部署，运行TPCDS测试，使用 spark-sql 执行 TPC-DS 查询）
- flink：band_width提升6.58%，验证场景nexmark（运行模式为streaming流处理模式，持续向flink注入事件，测试场景为q0）
- ceph：band_width提升7.82%，验证场景rados（一个主节点，三个从节点，运行bench基准测试，持续向存储池中写数据）
- nginx：RPS提升26.40%，验证场景httpress（单机部署，默认编译参数，worker_processes=auto，并发连接数512，并行线程数7，总请求数2000万次）
- oceanbase: QPS提升6.79%，验证场景sysbench（一个obproxy节点，三个observer节点，在租户数据库中创建10张测试表，每张表插入5000行测试数据，并发线程32，进行随机SELECT查询）

## 安装部署
提供四种安装方式，包括源码安装、源码服务方式安装、RPM包安装、容器安装（适用于oe2003低版本OS）。

### 方法一：源码安装

#### 1. 获取 gitee 源码
* 下载地址 https://gitee.com/openeuler/A-Tune/tree/euler-copilot-tune/
* 分支指定为 euler-copilot-tune
```bash
git clone https://gitee.com/openeuler/A-Tune.git
cd A-Tune/
# 切换到 euler-copilot-tune 分支
git checkout euler-copilot-tune
```

#### 2. 安装系统依赖
* 安装 python venv 依赖（调优程序运行机器）
```bash
yum install python3-devel krb5-devel
```
* 安装调优依赖并重启 sysstat（目标应用所在机器）
```bash
yum install sysstat perf ethtool
systemctl start sysstat
```

#### 3. 创建虚拟环境 & 安装依赖（调优程序运行机器）
* 创建并激活虚拟环境 venv
```bash
python3 -m venv venv
source venv/bin/activate
```
* 安装python依赖包
```bash
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 4. 修改配置文件
* 在项目的 config 文件夹中修改配置文件，具体内容参考[使用指南](#使用指南)

#### 5. 运行 EulerCopilot Tune
```bash
export PYTHONPATH="`pwd`:$PYTHONPATH"
python3 src/start_tune.py
```

### 方法二：源码服务方式安装
#### 1. 获取 gitee 源码（同方法一）

#### 2. 安装系统服务
* 进入项目目录执行
```bash
python setup.py install
```

#### 3. 修改配置文件
* 在 /etc/euler-copilot-tune 目录修改配置文件，具体内容参考[使用指南](#使用指南)

#### 4. 启动服务
* 开启调优主程序
```bash
euler-copilot-tune
```

* 启动 MCP servers
```bash
systemctl start tune-mcpserver
journalctl -xe -u tune-mcpserver --all -f
```

* 启动 OpenAPI
```bash
systemctl start tune-openapi
journalctl -xe -u tune-openapi --all -f
```

### 方法三：RPM 包方式安装
#### 1. 下载 RPM 包
* 地址：[https://eulermaker.compass-ci.openeuler.openatom.cn/package/download?osProject=houxu:openEuler-24.03-LTS-SP2:epol&packageName=euler-copilot-tune](https://gitee.com/link?target=https%3A%2F%2Feulermaker.compass-ci.openeuler.openatom.cn%2Fpackage%2Fdownload%3FosProject%3Dhouxu%3AopenEuler-24.03-LTS-SP2%3Aepol%26packageName%3Deuler-copilot-tune)

#### 2. 设置pip镜像源
* 由于RPM 安装过程需要使用 pip 下载资源，为了加快安装速度，推荐设置镜像源
```bash
pip config set global.index-url https://repo.huaweicloud.com/repository/pypi/simple/

# 清华大学TUNA镜像源： https://pypi.tuna.tsinghua.edu.cn/simple
# 阿里云镜像源： http://mirrors.aliyun.com/pypi/simple/
# 中国科学技术大学镜像源： https://mirrors.ustc.edu.cn/pypi/simple/
# 华为云镜像源： https://repo.huaweicloud.com/repository/pypi/simple/
# 腾讯云镜像源：https://mirrors.cloud.tencent.com/pypi/simple/
```

#### 3. 安装 RPM 包
注意：不要在 python 虚拟环境中执行，在系统环境下安装 pip 包  
* x86 架构
```bash
dnf install euler-copilot-tune-1.0-1.oe2403sp2.x86_64.rpm
```
* ARM 架构
```bash
dnf install euler-copilot-tune-1.0-1.oe2403sp2.aarch64.rpm
```  
* 查看详细日志
安装过程中会在Running scriptlet: euler-copilot-tune-1.0-1.x86_64 处停留较长时间，此处是在pip安装对应依赖包，可以通过如下命令查看详细日志
```bash
tail -f /pip_install.log
``` 
* 如果安装完成后出现 pip 包安装失败情况，请单独执行如下命令进行安装：
```bash
pip install  fastapi numpy openai paramiko pydantic pyyaml scikit-learn tqdm uvicorn requests langchain langchain-openai email-validator httpx tabulate gssapi pandas faiss-cpu pyfiglet mcp
``` 

#### 4. 修改配置文件
* 在 /etc/euler-copilot-tune 目录修改配置文件，具体内容参考[使用指南](#使用指南)

#### 5. 启动服务
* 开启调优主程序
```bash
euler-copilot-tune
```

* 启动 MCP servers
```bash
systemctl start tune-mcpserver
journalctl -xe -u tune-mcpserver --all -f
```

* 启动 OpenAPI
```bash
systemctl start tune-openapi
journalctl -xe -u tune-openapi --all -f
```

### 方法四：容器化部署

#### 1. 下载容器镜像

https://gitee.com/hubin95/euler-copilot-tune-container

- 包含 euler-copilot-tune.tar.gz00 ~ euler-copilot-tune.tar.gz04 共5个镜像分片文件。

#### 2. 导入容器镜像

```bash
# 合并、解压容器镜像
cat euler-copilot-tune.tar.gz0* > euler-copilot-tune.tar.gz
gzip -d euler-copilot-tune.tar.gz

# 导入容器镜像
docker load -i euler-copilot-tune.tar

# 修改镜像tag
docker tag <image_id> euler-copilot-tune:latest（*image_id* 替换成 docker images 命令查询到的id）
```

#### 3. 部署容器

```bash
docker run -p 8092:8092 euler-copilot-tune
```

#### 4. 运行Copilot调优

-   进入容器：

```bash
docker exec -it <docker id> /bin/bash  # <docker id>为前一步docker run返回的容器id
```

-   修改配置：

容器内的项目路径为 /app/euler-copilot-tune，在项目的 config 文件夹中修改配置文件，具体内容参考[使用指南](https://gitee.com/openeuler/A-Tune/blob/euler-copilot-tune/README.md#使用指南)

-   运行 EulerCopilot Tune：

```
cd /app/euler-copilot-tune
export PYTHONPATH="`pwd`:$PYTHONPATH"
python3 src/start_tune.py
```

## 使用指南
### 配置文件准备
#### 1. 修改 .env.yaml 配置文件内容（项目 config 目录下）
```bash
vim config/.env.yaml
```
* 具体格式如下： （**调优提升目标**的配置见其中的 feature - slo_goal 字段说明）
```YAML
# 根据实际使用的模型服务填写以下字段
LLM_KEY: "sk-XXXXXX"                  # 必填：模型服务的 API 密钥
LLM_URL: "https://api.deepseek.com"   # 必填：LLM 服务的 API 接口地址，如 "https://api.deepseek.com"
LLM_MODEL_NAME: "deepseek-chat"       # 必填：要调用的模型名，如 deepseek-chat
LLM_MAX_TOKENS:                       # 选填：生成文本的最大 token 数，如512或2048

REMOTE_EMBEDDING_ENDPOINT: "https://api.embedding.com/v1/embeddings"  # 嵌入模型服务地址
REMOTE_EMBEDDING_MODEL_NAME: "bge-large-zh"                           # 嵌入模型名称，如 text-embedding-3-small、bge-large-zh
 
servers:
  - ip: ""                                                              # 应用所在ip
    host_user: ""                                                       # 登录机器的usr id
    password: ""                                                        # 登录机器的密码
    port:                                                               # 应用所在ip的具体port
    app: "mysql"                                                        # 当前支持mysql、nginx、pgsql、spark
    listening_address: ""                                               # 应用监听的ip(当前仅flink、nginx、spark需要填写)
    listening_port: ""                                                  # 应用监听的端口(当前仅flink、nginx、spark需要填写)
    target_process_name: "mysqld"                                       # 调优应用的name
    business_context: "高并发数据库服务，CPU负载主要集中在用户态处理"           #调优应用的描述（用于策略生成）
    max_retries: 3
    delay: 1.0
    
feature:
  - need_restart_application: False                                     # 修改参数之后是否需要重启应用使参数生效
    need_recover_cluster: False                                         # 调优过程中是否需要恢复集群
    microDep_collector: True                                            # 是否开启微架构指标采集
    pressure_test_mode: True                                            # 是否通过压测模拟负载环境
    tune_system_param: False                                            # 是否调整系统参数
    tune_app_param: True                                                # 是否调整应用参数
    strategy_optimization: False                                        # 是否需要策略推荐
    benchmark_timeout: 3600                                             # benchmark执行超时限制
    max_iterations: 10                                                  # 最大迭代轮数
    slo_goal: 0.1                                                       # 调优提升目标，默认0.1也即10%，调优达成提升目标后会提前结束

```

#### 2. 完善 app_config.yaml（项目 config 目录下）  
(需按实际环境修改，重点关注 set_param_template、 get_param_template、 benchmark 脚本)  
* set_param_template：设置应用配置参数（copilot调优时，会使用此脚本修改参数值）  
```YAML
# 说明：
#   - $param_name：将被copilot替换为待修改的参数名（如 worker_connections）
#   - $param_value：将被copilot替换为参数目标值（如 8192）
#   - $config_file：指向应用配置文件路径（已在 config 中定义）

# 示例（mysql）：
set_param_template: 'grep -q "^$param_name\\s*=" "$config_file" && sed -i "s/^$param_name\\s*=.*/$param_name = $param_value/" "$config_file" || sed -i "/\\[mysqld\\]/a $param_name = $param_value" "$config_file"'
```

* get_param_template：获取应用配置参数  
```YAML
# 说明：
#   - $param_name：将被copilot替换为参数名

# 示例（mysql）：
get_param_template: 'grep -E "^$param_name\\s*=" $config_file | cut -d= -f2- | xargs'
```

* benchmark：压测命令模版
```YAML  
# 说明：
#   - $EXECUTE_MODE:local    → 在 Copilot 控制机本地执行
#   - $EXECUTE_MODE:remote   → 通过 SSH 跳转到目标机器执行，默认使用remote执行模式
#   - 其他变量（如 $host_ip, $port, $user）将被自动替换

# 示例（mysql）：
benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/mysql/parse_benchmark.sh $host_ip $port $user $password"
```

* __完整配置示例如下：__
```YAML
mysql:
  user: "root"
  password: "123456"
  config_file: "/etc/my.cnf"
  port: 3306
  set_param_template: 'grep -q "^$param_name\\s*=" "$config_file" && sed -i "s/^$param_name\\s*=.*/$param_name = $param_value/" "$config_file" || sed -i "/\\[mysqld\\]/a $param_name = $param_value" "$config_file"'
  get_param_template: 'grep -E "^$param_name\s*=" $config_file | cut -d= -f2- | xargs'
  stop_workload: "systemctl stop mysqld"
  start_workload: "systemctl start mysqld"
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/mysql/parse_benchmark.sh $host_ip $port $user $password"
  performance_metric: "QPS"

flink:
  set_param_template: '/patch/to/script/set_param.sh $param_name $param_value'
  get_param_template: '/patch/to/script/get_param.sh $param_name'
  benchmark: "/patch/to/script/nexmark_test.sh"
  stop_workload: 'docker exec -i flink_jm_8c32g bash -c "source /etc/profile && /usr/local/flink-1.16.3/bin/stop-cluster.sh && /usr/local/nexmark/bin/shutdown_cluster.sh"'
  start_workload: 'docker exec -i flink_jm_8c32g bash -c "source /etc/profile && /usr/local/flink-1.16.3/bin/start-cluster.sh"'
  performance_metric: "THROUGHPUT"

pgsql:
  user: "postgres"
  password: "postgres"
  config_file: "/data/data1/pgsql/postgresql.conf"
  port: 5432
  set_param_template: 'grep -qE "^\s*$param_name\s*=" "$config_file" && sed -i "s/^[[:space:]]*$param_name[[:space:]]*=.*/$param_name = $param_value/" "$config_file" || echo "$param_name = $param_value" >> "$config_file"'
  get_param_template: 'grep -oP "^\s*$param_name\s*=\s*\K.*" "$config_file"'
  stop_workload: "su - postgres -c '/usr/local/pgsql/bin/pg_ctl stop -D /data/data1/pgsql/ -m fast'"
  start_workload: "su - postgres -c '/usr/local/pgsql/bin/pg_ctl start -D /data/data1/pgsql/ -l /var/log/postgresql/postgresql.log'"
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/postgresql/parse_benchmark.sh $host_ip $port $user $password"
  performance_metric: "QPS"

spark:
  set_param_template: 'sh /path/of/set_param.sh $param_name $param_value'
  get_param_template: 'sh /path/of/get_param.sh $param_name'
  benchmark: "sh /path/of/spark_benchmark.sh"
  performance_metric: "DURATION"

nginx:
  port: 10000
  config_file: "/usr/local/nginx/conf/nginx.conf"
  set_param_template: 'grep -q "^\\s*$param_name\\s\\+" "$config_file" && sed -i "s|^\\s*$param_name\\s\\+.*|    $param_name $param_value;|" "$config_file" || sed -i "/http\\s*{/a\    $param_name $param_value;" "$config_file"'
  get_param_template: 'grep -E "^\\s*$param_name\\s+" $config_file | head -1 | sed -E "s/^\\s*$param_name\\s+(.*);/\\1/"'
  stop_workload: "/usr/local/nginx/sbin/nginx -s reload"
  start_workload: "/usr/local/nginx/sbin/nginx -s reload"
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/nginx/parse_benchmark.sh $host_ip $port"
  performance_metric: "QPS"

ceph:
  set_param_template: 'ceph config set osd "$param_name" "$param_value"'
  get_param_template: 'sh /path/of/get_params.sh'
  start_workload: "sh /path/of/restart_ceph.sh"
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/ceph/parse_benchmark.sh"
  performance_metric: "BANDWIDTH"

gaussdb:
  user: ""
  password: ""
  config_file: "/path/of/config_file"
  port: 5432
  set_param_template: 'gs_guc set -Z datanode  -N all -I all -c "${param_name}=${param_value}"'
  get_param_template: 'gs_guc check -Z datanode -N all -I all -c "${param_name}"'
  stop_workload: "cm_ctl stop -m i"
  start_workload: "cm_ctl start"
  recover_workload: "$EXECUTE_MODE:local sh /path/of/gaussdb_cluster_recover.sh"
  benchmark: "$EXECUTE_MODE:local sh/path/of/gaussdb_benchmark.sh"
  performance_metric: "DURATION"

system:
  set_param_template: 'sysctl -w $param_name=$param_value'
  get_param_template: 'sysctl $param_name'

redis:
  port: 6379
  config_file: "/etc/redis.conf"
  set_param_template: "sed -i 's/^$param_name/$param_name $param_value/g' $config_file"
  get_param_template: "grep -P '$param_name' $config_file | awk '{print $2}"
  start_workload: "systemctl start redis"
  stop_workload: "systemctl stop redis"
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/redis/parse_benchmark.sh $host_ip $port "
  performance_metric: "QPS"

```

#### 3. benchmark.sh 脚本具体内容如下：
```YAML
#（必须有）用于通知框架可以执行指标采集的标识
echo 1 > /tmp/euler-copilot-fifo  

# benchmark 具体执行
cd /root/spark_auto_deploy_arm/spark_test
sh tpcds_test_1t_spark331_linearity_2p.sh > /home/cxm/spark_benchmark.log 2>&1

#（必须有）计算并输出相应的 performance_metric 的语句
cd /home/cxm
time_taken=$(grep "time_taken:" "spark_benchmark.log" | sed -E 's/.*time_taken:([0-9.]+)s.*/\1/' | paste -sd+ | bc | xargs printf "%.2f")
echo $time_taken
```

### 应用示例
* [mysql 应用验证示例](doc/zh/mysql.md)
* [spark 应用验证示例](doc/zh/spark.md)
* [ceph 应用验证示例](doc/zh/ceph.md)
* [nginx 应用验证示例](doc/zh/nginx.md)
* [flink 应用验证示例](doc/zh/flink.md)
* [oceanbase 应用验证示例](doc/zh/oceanbase.md)

## OS领域模型部署指南

### 模型介绍

openEuler提供了一个针对智能调优场景而微调泛化构建的领域模型，支持纯CPU部署推理。

OS_model模型基于qwen3-4b模型微调，使用了云大数存场景历史性能调优语料进行微调。

在大数据spark、数据库pgsql/mysql、分布式存储ceph、虚拟化nginx应用上分别测试了领域模型、deepseek_v31(671b)与qwen3-4b原始模型，效果如下：

1、领域模型调优相比开箱性能在大数据spark上提升15%+，数据库pgsql/mysql上提升50%+，虚拟化nginx上提升150%+、分布式存储ceph上提升50%+；

2、领域模型相对于满血版deepseek效果持平，在部分应用上略优于deepseek满血版，全面领先qwen3-4b；

3、领域模型量化到INT4规模，纯CPU部署情况下，相比FP16规模吞吐率提升2倍，达到小时级调优，且性能基本无损。

详见： [openEuler Intelligence OS领域模型](https://ai.gitee.com/openEuler-Intelligence/openEuler-Intelligence-OS_model)

### 模型容器化一键部署

#### 文件下载
 - 容器底座container-llama下载：
     - https://gitee.com/openEuler-Intelligence/container-llama.cpp/raw/master/b6602-kunpeng920.tar.aa
     - https://gitee.com/openEuler-Intelligence/container-llama.cpp/raw/master/b6602-kunpeng920.tar.ab
 - 领域模型文件下载地址：https://ai.gitee.com/openEuler-Intelligence/openEuler-Intelligence-OS_model/tree/master
     - PS：openEuler-Intelligence-OS_model-IQ4_NL-00001-of-00009 ~ openEuler-Intelligence-OS_model-IQ4_NL-00009-of-00009，共9个文件都需要下载。

#### 加载container-llama容器镜像
```BASH
# 加载容器镜像
cat b6602-kunpeng920.tar.a* > llama.cpp_arm64.tar
docker load -i llama.cpp_arm64.tar

# 查看images
docker images

# 修改镜像tag
docker tag *image_id* llama.cpp_arm64:b6602（*image_id* 替换成 docker images 命令查询到的id）
```

#### 拉起领域模型
上传领域模型的9个文件至/root/models（也可以自定义路径，后续命令中-v参数相应调整），执行：
```BASH
docker run -d -p 11434:11434 -v /root/models:/models llama.cpp_arm64:b6602 -m /models/openEuler-Intelligence-OS_model-IQ4_NL-00001-of-00009.gguf --host 0.0.0.0 --port 11434
```
PS：若容器拉起时遇到报错 operation not permitted，可以在 docker run 命令后增加参数 --security-opt seccomp=unconfined 解决。

#### 验证测试
```bash
curl 'http://127.0.0.1:11434/v1/chat/completions' \
--header 'Content-Type: application/json' \
--data '{
    "model": "openEuler-Intelligence-OS_model",
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "stream": false
  }'
```


## 常见问题解决

见 [FAQ.md](./FAQ.md)