# EulerCopilot Tune 安装与使用指南

## 项目简介
EulerCopilot Tune 通过采集系统、微架构、应用等维度的指标数据，结合大语言模型与定制化 Prompt 工程，针对不同应用的可调参数给出可靠的参数推荐。同时，根据推荐的参数运行 benchmark 并与 baseline 进行对比，可以计算出推荐参数对应用性能的提升值。

## 安装部署
提供三种安装方式，包括源码安装、源码服务方式安装以及RPM包安装。

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
yum install sysstat perf
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
* 如果按照完成后出现 pip 包安装失败情况，请单独执行如下命令进行安装：
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
## 使用指南
### 配置文件准备
#### 1. 修改 .env.yaml 配置文件内容（项目 config 目录下）
```bash
vim config/.env.yaml
```
* 具体格式如下：
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
#   - $EXECUTE_MODE:remote   → 通过 SSH 跳转到目标机器执行
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


## 常见问题解决

见 [FAQ.md](./FAQ.md)