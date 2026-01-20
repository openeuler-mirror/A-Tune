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

### （调优前提）调优目标环境部署

1. 部署应用，保证应用处于运行状态。
2. 明确应用配置文件：例如mysql默认为 /etc/my.cnf。
3. 明确参数修改方法：例如修改应用配置文件中的字段值。
4. 明确参数修改是否需重启生效：若需要，则明确启停命令，例如mysql可通过 systemctl start mysqld/systemctl stop mysqld 命令启动或停止。
5. 准备压测脚本：benchmark.sh（名称不限制），保证运行benchmark.sh可成功执行压测，并且性能指标在日志输出中。调优前建议先手动测试，验证可跑通。

### 配置copilot调优

#### 1. 修改 .env.yaml 配置文件内容（项目 config 目录下）

根据调优需要，修改相应配置字段：
```bash
vim config/.env.yaml
```

* 具体格式如下： （**调优提升目标**的配置见其中的 feature - slo_goal 字段说明）
```YAML
# 根据实际使用的模型服务填写以下字段
LLM_KEY: "sk-XXXXXX"                  # 必填：模型服务的 API 密钥
LLM_URL: "https://api.deepseek.com"   # 必填：LLM 服务的 API 接口地址，如 "https://api.deepseek.com"
LLM_MODEL_NAME: "deepseek-chat"       # 必填：要调用的模型名，如 deepseek-chat
LLM_MAX_TOKENS: 8192                  # 选填：生成文本的最大 token 数，如4096，根据模型能力调整

REMOTE_EMBEDDING_ENDPOINT: "https://api.embedding.com/v1/embeddings"  # 选填：嵌入模型服务地址
REMOTE_EMBEDDING_MODEL_NAME: "bge-large-zh"                           # 选填：嵌入模型名称，如 text-embedding-3-small、bge-large-zh
 
servers:
  - ip: ""                                                              # 必填：调优目标机器ip
    host_user: ""                                                       # 必填：调优目标机器SSH登录用户
    password: ""                                                        # 必填：调优目标机器SSH登录密码
    port: 22                                                            # 必填：调优目标机器SSH连接port
    app: "mysql"                                                        # 必填：调优目标应用，当前支持的应用见 config/app_config.yaml 中已定义的字段
    listening_address: ""                                               # 选填：应用监听的ip(当前仅flink、nginx、spark需要填写)
    listening_port: ""                                                  # 选填：应用监听的端口(当前仅flink、nginx、spark需要填写)
    target_process_name: "mysqld"                                       # 选填：调优应用进程名，使能微架构分析时必须填写
    business_context: "高并发数据库服务，CPU负载主要集中在用户态处理"       # 选填：调优应用的描述，启用调优策略推荐时必须填写
    
feature:
  - need_restart_application: True                                      # True/False，表示是否需要重启应用以使参数修改生效
    need_recover_cluster: False                                         # True/False，表示是否需要恢复集群以使参数修改生效
    microDep_collector: True                                            # True/False，表示是否开启微架构指标采集，虚拟化环境不支持无需开启
    pressure_test_mode: True                                            # True/False，表示是否通过压测模拟负载环境，若系统自带负载无需压测打流，则可关闭
    tune_system_param: False                                            # True/False，表示是否调整系统参数，若打开，则调优范围增加系统参数，因调优效果一般不如应用参数效果明显，默认关闭
    tune_app_param: True                                                # True/False，表示是否调整应用参数，若打开，则调优范围增加应用参数，优先调优此类参数，注：应用参数与系统参数调优必须至少打开一个
    strategy_optimization: False                                        # True/False，表示是否启用策略推荐，注：调优策略无法自动化使能，推荐仅供参考
    benchmark_timeout: 3600                                             # 正整数，单位秒，表示benchmark执行超时限制
    max_iterations: 10                                                  # 正整数，单位秒，表示最大迭代轮数
    slo_goal: 0.1                                                       # 浮点数，表示调优提升目标，默认0.1也即10%，若调优迭代过程中已达成提升目标，则提前结束迭代
    best_param_save_path: "best_params.json"                            # 绝对/相对路径，表示最优参数保存文件路径
    data_dir: "data"                                                    # 绝对/相对路径，表示中间数据的文件夹路径
    save_snapshot: False                                                # True/False，表示是否保存快照，也即保存采集、分析、调优初始化等步骤结果快照，保存路径为 ${data_dir}/snapshot/
    use_snapshot: False                                                 # True/False，表示是否使用快照，也即跳过采集、分析、调优初始化等步骤，直接使用已保存结果快照
    max_retries: 3                                                      # 正整数，表示执行命令的失败重试次数
    delay: 1.0                                                          # 浮点数，表示执行命令的失败重试间隔
```

#### 2. 修改 app_config.yaml 文件内容（项目 config 目录下）  
(需按实际环境修改，重点关注 version、set_param_template、get_param_template、benchmark 配置）

* version：应用版本（用于copilot选取对应最近版本的调优参数知识库）
```YAML  
# 示例（mysql）：
version: "v5.7"

# 说明：版本号必须以 v 开头，例如 v{x}.{y}.{z}，可参考 app_config.yaml 中各应用的默认配置。
```

* set_param_template：参数设置方法（copilot调优时，会在调优机器以bash运行此方法修改参数值） 
```YAML
# 示例（mysql）：
set_param_template: 'grep -q "^$param_name\\s*=" "$config_file" && sed -i "s/^$param_name\\s*=.*/$param_name = $param_value/" "$config_file" || sed -i "/\\[mysqld\\]/a $param_name = $param_value" "$config_file"'

# 说明：
#   - $param_name：将被copilot替换为待修改的参数名（如 worker_connections）
#   - $param_value：将被copilot替换为参数目标值（如 8192）
#   - $config_file：指向应用配置文件路径（使用 config 中定义的值）
```

* get_param_template：参数获取方法（copilot调优时，会在调优机器以bash运行此方法获取参数值） 
```YAML
# 示例（mysql）：
get_param_template: 'grep -E "^$param_name\\s*=" $config_file | cut -d= -f2- | xargs'

# 说明：
#   - $param_name：将被copilot替换为参数名（如 worker_connections）
```

* benchmark：性能指标获取方法（copilot调优时，会在调优机器或本地运行此方法获取性能指标）
```YAML  
# 示例（mysql）：
benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/mysql/parse_benchmark.sh $host_ip $port $user $password"

# 说明：
#   $EXECUTE_MODE：表示命令执行模式
#   - $EXECUTE_MODE:local    → 在 Copilot 部署机器本地执行
#   - $EXECUTE_MODE:remote   → 通过 SSH 跳转到调优目标机器执行，默认使用remote执行模式
#   其他变量：
#   - $SCRIPTS_DIR 会自动展开为 copilot 项目内置脚本目录路径，其中保存有一些应用示例，也即 ${copilot_tune_dir}/scripts 目录
#   - $host_ip, $port, $user 会自动替换为 config 中定义的值
```
parse_benchmark.sh 建议写法：
1.运行benchmark.sh，日志重定向到benchmark.log；
2.从benchmark.log中提取性能指标输出。

parse_benchmark.sh 示例：
假设mysql benchmark.sh 输出如下格式：
```
...
SQL statistics:
    queries performed:
        read:                            0
        write:                           221668
        other:                           110834
        total:                           332502
    transactions:                        55417  (306.88 per sec.)
    queries:                             332502 (1841.30 per sec.)
    ignored errors:                      0      (0.00 per sec.)
    reconnects:                          0      (0.00 per sec.)
...
```
mysql指标为queries per second，也即queries行中的数字 1841.30，则 mysql parse_benchmark.sh 可编写如下：
```bash
#!/bin/bash
SCRIPT_PATH="$(realpath "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
cd "$SCRIPT_DIR"
sh benchmark.sh $1 $2 $3 $4 > benchmark.log 2>&1

# extract performance metric from log
grep "queries:" benchmark.log | awk -F'[()]' '{print $2}' | awk '{print $1}'
# 说明：
# grep "queries:" benchmark.log 表示过滤包含 queries 的一行，得到 【queries:         332502 (1841.30 per sec.)】
# awk -F'[()]' '{print $2}' 表示提取以 '()' 作为分隔后的第2个字符串，得到 【1841.30 per sec.】
# awk '{print $1}' 表示提前以空格作为分隔后的第1个字符串，得到 【1841.30】
```
运行copilot前，建议手动运行 parse_benchmark.sh 以确认输出指标值正确性。

* __mysql应用配置示例如下：__
```YAML
mysql:
  version: "v5.7"
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
```

#### 3. benchmark.sh 脚本具体内容参考如下：
```YAML
#（必须有）用于通知框架可以执行指标采集的标识
echo 1 > /tmp/euler-copilot-fifo  

#（必须有）benchmark 具体执行
cd /root/spark_auto_deploy_arm/spark_test
sh tpcds_test_1t_spark331_linearity_2p.sh > /root/spark_auto_deploy_arm/spark_benchmark.log 2>&1

#（必须有）计算并输出相应的 performance_metric 的语句
cd /root/spark_auto_deploy_arm
time_taken=$(grep "time_taken:" "spark_benchmark.log" | sed -E 's/.*time_taken:([0-9.]+)s.*/\1/' | paste -sd+ | bc | xargs printf "%.2f")
echo $time_taken
```
注：此脚本的输出用于Copilot获取性能指标值，必须为纯数字，不能带其他文本输出，若有输出则需重定向到文件中。

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
docker run -d -p 11434:11434 -v /root/models:/models llama.cpp_arm64:b6602 -s -m /models/openEuler-Intelligence-OS_model-IQ4_NL-00001-of-00009.gguf --host 0.0.0.0 --port 11434
```
920机器推理性能优化参数：（需32核、6GB内存）
```BASH
docker run -d -p 11434:11434 -v /root/models:/models llama.cpp_arm64:b6602 -s -m /models/openEuler-Intelligence-OS_model-IQ4_NL-00001-of-00009.gguf --host 0.0.0.0 --port 11434 -np 4 -t 32 --numa distribute --cpu-strict 1 --prio 2 --swa-full --cache-type-k q4_1 --log-disable --ctx-size 10240
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
输出示例：
```
{"choices":[{"finish_reason":"stop","index":0,"message":{"role":"assistant","content":"你好！有什么问题我可以帮助你吗？😊"}}],"created":1768872866,"model":"openEuler-Intelligence-OS_model","system_fingerprint":"b0-unknown","object":"chat.completion","usage":{"completion_tokens":11,"prompt_tokens":9,"total_tokens":20},"id":"chatcmpl-mZP5NbcmQjvZudnYovlQORru3E1EBRTV","timings":{"cache_n":0,"prompt_n":9,"prompt_ms":776.921,"prompt_per_token_ms":86.32455555555556,"prompt_per_second":11.584189383476568,"predicted_n":11,"predicted_ms":5233.48,"predicted_per_token_ms":475.7709090909091,"predicted_per_second":2.101851922621277}}
```

## 常见问题解决

见 [FAQ.md](./FAQ.md)