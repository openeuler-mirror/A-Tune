# oceanbase部署文档（包含sysbench压测命令）
https://www.hikunpeng.com/document/detail/zh/kunpengdbs/ecosystemEnable/OceanBase/kunpengocenbase_04_0001.html
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
  # OBServer 节点 1
  - ip: ""
    host_user: ""
    password: ""
    port: 22
    app: "oceanbase"
    target_process_name: "observer"
    business_context: "OceanBase Server 节点 1，负责数据存储与计算"
    max_retries: 3
    delay: 1.0

  # OBServer 节点 2
  - ip: ""
    host_user: ""
    password: ""
    port: 22
    app: "oceanbase"
    target_process_name: "observer"
    business_context: "OceanBase Server 节点 2，负责数据存储与计算"
    max_retries: 3
    delay: 1.0

  # OBServer 节点 3
  - ip: ""
    host_user: ""
    password: ""
    port: 22
    app: "oceanbase"
    target_process_name: "observer"
    business_context: "OceanBase Server 节点 3，负责数据存储与计算"
    max_retries: 3
    delay: 1.0

  # Proxy 节点
  - ip: ""
    host_user: ""
    password: ""
    port: 22
    app: "oceanbase"
    target_process_name: "obproxy"
    business_context: "OceanBase Proxy 节点，负责 SQL 路由与连接负载均衡"
    max_retries: 3
    delay: 1.0
```
* __应用部署信息 config/app_config.yaml 配置__        
需按实际环境填写；一般无需修改，若部署方式不同需要修改对应命令。
```YAML
oceanbase:
  user: "root@sysbench_tenant"
  password: ""
  config_file: "/root/.obd/cluster/obcluster/config.yaml"
  port: 2881
  set_param_template: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/oceanbase/set_param.sh $param_name $param_value"
  get_param_template: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/oceanbase/get_param.sh $param_name"
  stop_workload: "obd cluster stop obcluster"
  start_workload: "obd cluster start obcluster"
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/oceanbase/parse_benchmark.sh"
  performance_metric: "QPS"
```
* get_param.sh 脚本内容：
```YAML
#!/bin/bash
# 功能：根据参数 scope 自动选择 observer / obproxy 查询参数
# 用法：
#  初始设置时
#   ./get_param.sh <param_name> <observer_ip> <observer_password> <proxy_ip> <proxy_password> <copilot_path>
#  参数获取时：
#   ./get_param.sh <param_name>

PARAM=$1
OBSERVERIP=$2
OBSERVERPD=$3
PROXYIP=$4
PROXYPD=$5
COPILOTPATH=$6

# ===== 用户配置区 =====
OBCLIENT_OBSERVER="obclient -h$OBSERVERIP -P2881 -uroot@sys -p$OBSERVERPD -Doceanbase -A"
OBCLIENT_PROXY="obclient -h$PROXYIP -P2883 -uroot@proxysys -p$PROXYPD -Doceanbase -A"
PARAM_FILE="$COPILOTPATH/A-Tune-euler-copilot-tune/src/knowledge_base/knob_params/oceanbase.json"
# =======================

if [ $# -lt 1 ]; then
    echo "用法：$0 <param_name>"
    exit 1
fi

# 校验参数文件
if [ ! -f "$PARAM_FILE" ]; then
    echo "错误：找不到参数文件 $PARAM_FILE"
    exit 1
fi

# 从 JSON 提取 scope
SCOPE=$(jq -r --arg name "$PARAM" '.[$name].scope' "$PARAM_FILE")

if [ "$SCOPE" == "null" ] || [ -z "$SCOPE" ]; then
    echo "❌  未在参数文件中找到 $PARAM"
    exit 1
fi

# ---------- 查询 ----------
case "$SCOPE" in
  observer)
    REMOTE_CMD="$OBCLIENT_OBSERVER -e \"SHOW PARAMETERS LIKE '$PARAM';\" | awk 'NR>3 && \$1==\"zone2\"{print \$7}'"
    ssh -q root@$OBSERVERIP "$REMOTE_CMD"
    ;;
  obproxy)
    REMOTE_CMD="$OBCLIENT_PROXY -e \"SHOW PROXYCONFIG LIKE '$PARAM';\" | awk -v name=\"$PARAM\" '\$1==name{print \$2}'"
    ssh -q root@$OBSERVERIP "$REMOTE_CMD"
    ;;
  *)
    echo "❌  未知scope类型：$SCOPE"
    ;;
esac
```
* set_param.sh 脚本内容：
```YAML
#!/bin/bash
# 功能：根据参数 scope 自动选择 observer / obproxy 设置参数
# 用法：
#  初始设置时
#   ./set_param.sh <param_name> <value> <observer_ip> <observer_password> <proxy_ip> <proxy_password> <copilot_path>
#  参数设置时：
#   ./set_param.sh <param_name> <value>

PARAM=$1
VALUE=$2
OBSERVERIP=$3
OBSERVERPD=$4
PROXYIP=$5
PROXYPD=$6
COPILOTPATH=$7

# ===== 用户配置区 =====
OBCLIENT_OBSERVER="obclient -h$OBSERVERIP -P2881 -uroot@sys -p$OBSERVERPD -Doceanbase -A"
OBCLIENT_PROXY="obclient -h$PROXYIP -P2883 -uroot@proxysys -p$PROXYPD -Doceanbase -A"
PARAM_FILE="$COPILOTPATH/A-Tune-euler-copilot-tune/src/knowledge_base/knob_params/oceanbase.json"
# =======================

if [ $# -lt 2 ]; then
    echo "用法：$0 <param_name> <value>"
    exit 1
fi

# 校验参数文件
if [ ! -f "$PARAM_FILE" ]; then
    echo "错误：找不到参数文件 $PARAM_FILE"
    exit 1
fi

# 从 JSON 提取 scope
SCOPE=$(jq -r --arg name "$PARAM" '.[$name].scope' "$PARAM_FILE")

if [ "$SCOPE" == "null" ] || [ -z "$SCOPE" ]; then
    echo "❌  未在参数文件中找到 $PARAM"
    exit 1
fi

# ---------- 设置 ----------
case "$SCOPE" in
  observer)
    REMOTE_CMD="$OBCLIENT_OBSERVER -e \"ALTER SYSTEM SET $PARAM = $VALUE;\""
    ssh -q root@$OBSERVERIP "$REMOTE_CMD"
    ;;
  obproxy)
    REMOTE_CMD="$OBCLIENT_PROXY -e \"ALTER PROXYCONFIG SET $PARAM = $VALUE;\""
    ssh -q root@$OBSERVERIP "$REMOTE_CMD"
    ;;
  *)
    echo "❌  未知scope类型：$SCOPE"
    ;;
esac
```

* __scripts/oceanbase/benchmark.sh 脚本内容：__
```YAML
echo 1 > /tmp/euler-copilot-fifo
obd test sysbench obcluster --tenant=sysbench_tenant --script-name=oltp_read_only.lua --tables=30 --table-size=10000 --threads=32
```

## 4. 执行调优程序
```bash
# 在源码根目录执行
export PYTHONPATH="`pwd`:$PYTHONPATH"
python3 src/start_tune.py
```