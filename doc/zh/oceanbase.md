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
  set_param_template: "sh xxx/set_param.sh $param_name $param_value"
  get_param_template: "grep -P '$param_name' $config_file | awk '{print $2;exit}'"
  stop_workload: "obd cluster stop obcluster"
  start_workload: "obd cluster start obcluster"
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/oceanbase/parse_benchmark.sh"
  performance_metric: "QPS"
```
* set_param.sh 脚本内容：
```YAML
#!/bin/bash
# 需要把该脚本移动至oceanbase应用部署机器上

param_name=$1
param_value=$2
config_file="/root/.obd/cluster/obcluster/config.yaml"

# 如果参数已存在，只修改第一次出现的地方
if grep -q "^[[:space:]]*$param_name:" "$config_file"; then
  sed -i "0,/^[[:space:]]*$param_name:.*/s//  $param_name: $param_value/" "$config_file"
else
  # 如果不存在，在第一个 global: 后插入
  awk -v key="$param_name" -v val="$param_value" '
    BEGIN {inserted=0}
    /^  global:/ {
      print
      if (!inserted) {
        print "    " key ": " val
        inserted=1
      }
      next
    }
    {print}
  ' "$config_file" > /tmp/tmp_conf && mv /tmp/tmp_conf "$config_file"
fi
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