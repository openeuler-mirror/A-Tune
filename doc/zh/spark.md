# Spark部署文档（包含benchmark测试脚本）
https://www.hikunpeng.com/document/detail/zh/kunpengbds/ecosystemEnable/Spark/kunpengspark_04_0001.html
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
  - ip: ""                              # 服务器 IP
    host_user: ""                       # 登录用户
    password: ""                        # 登录密码（如果用密钥可留空）
    port: 22                            # SSH 端口（默认 22）
    app: "spark"                        # 应用类型（这里是 Spark）
    target_process_name: "java"         # Spark 进程名，一般是 java
    business_context: "基于内存计算的分布式批处理框架，适合大规模数据处理任务，CPU负载主要集中在用户态的序列化、>反序列化及任务调度执行过程"          # 业务上下文描述（例如：Spark SQL Benchmark）
    max_retries: 3                      # 最大重试次数
    delay: 1.0                          # 重试间隔（秒）
```
* __应用部署信息 config/app_config.yaml 配置__        
需按实际环境填写；一般无需修改，若部署方式不同需要修改对应命令。
```YAML
spark:
  set_param_template: 'sh /path/of/set_param.sh $param_name $param_value'
  get_param_template: 'sh /path/of/get_param.sh $param_name'
  benchmark: "sh /path/of/spark_benchmark.sh"
  performance_metric: "DURATION"
```
* set_param.sh 脚本内容：
```YAML
#!/bin/bash

param="$1"
value="$2"
config_file="/root/spark_auto_deploy_arm/spark_test/spark_params.sh"

# 参数检查
if [ -z "$param" ] || [ -z "$value" ]; then
    echo "Usage: $0 <param> <value>"
    echo "Examples:"
    echo "  $0 driver-cores 16"
    echo "  $0 spark.sql.shuffle.partitions 500"
    exit 1
fi

# 参数名合法性检查（允许 spark.xxx 或 xxx）
if ! [[ "$param" =~ ^[a-zA-Z0-9._-]+$ ]]; then
    echo "Error: Invalid parameter name: $param"
    exit 1
fi

# 文件存在性检查
if [ ! -f "$config_file" ]; then
    echo "Error: $config_file not found!"
    exit 1
fi

# 创建临时文件并设置清理
temp_file=$(mktemp)
trap 'rm -f "$temp_file"' EXIT

# 转义参数名（用于正则匹配）
escaped_param=$(printf '%s' "$param" | sed 's/[.[\*^$()+?{|]/\\&/g')

# 标记是否已替换
found=0

# 缩进：我们使用 2 个空格（根据你的文件结构）
indent="  "

# 遍历每一行，安全处理无换行结尾
while IFS= read -r line || [ -n "$line" ]; do

    # 情况1: --conf spark.xxx=...
    if [[ "$line" =~ ^[[:space:]]*--conf[[:space:]]+\"?$escaped_param= ]]; then
        if [ $found -eq 0 ]; then
            echo "${indent}--conf $param=$value" >> "$temp_file"
            found=1
        else
            echo "# Removed duplicate: $line" >&2
        fi
        continue
    fi

    # 情况2: --param value （如 --driver-cores 8）
    # 构造匹配模式：--driver-cores 后跟空格或tab，再跟任意值
    if [[ "$line" =~ ^[[:space:]]*--$escaped_param[[:space:]]+[^[:space:]]+ ]]; then
        if [ $found -eq 0 ]; then
            echo "${indent}--$param $value" >> "$temp_file"
            found=1
        else
            echo "# Removed duplicate: $line" >&2
        fi
        continue
    fi

    # 检查是否是 SPARK_OPERATOR_PARAMS 的结束括号 )
    if [[ "$line" =~ ^[[:space:]]*\)[[:space:]]*$ ]] && [ $found -eq 0 ]; then
        # 插入新参数
        if [[ "$param" == spark.* ]]; then
            echo "${indent}--conf $param=$value" >> "$temp_file"
        else
            echo "${indent}--$param $value" >> "$temp_file"
        fi
    fi

    # 输出原行
    echo "$line" >> "$temp_file"

done < "$config_file"

# 确保文件以换行结尾
sed -i -e '$a\' "$temp_file"

# 替换原文件
mv "$temp_file" "$config_file"

echo "Updated '$param' to '$value' in $config_file"

```
* get_param.sh 脚本内容：
```YAML
#!/bin/bash

param="$1"
execute_scripts="/xxx/spark_test/spark_params.sh"

if [ -z "$param" ]; then
    echo "Usage: $0 <param_name>"
    echo "Examples:"
    echo "  $0 spark.sql.shuffle.partitions"
    echo "  $0 driver-cores"
    echo "  $0 executor-memory"
    exit 1
fi

if [ ! -f "$execute_scripts" ]; then
    echo "Error: Config file not found: $execute_scripts" >&2
    exit 1
fi

# 安全提取 SPARK_OPERATOR_PARAMS 内容
params=$(awk '
    /SPARK_OPERATOR_PARAMS=\(/, /\)/ {
        if (!/SPARK_OPERATOR_PARAMS=\(/ && !/\)/) print
    }
' "$execute_scripts")

# 查找参数并提取值
while IFS= read -r line; do
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

    # 情况1: --conf spark.xxx=yyy
    if [[ "$line" =~ --conf[[:space:]]*[\"\']?([a-zA-Z0-9._-]+)=([^\"]*) ]]; then
        key="${BASH_REMATCH[1]}"
        val="${BASH_REMATCH[2]}"
        # ✅ 修复：一步删除末尾引号+空格
        val=$(echo "$val" | sed -e "s/[\"'][[:space:]]*\$//")
        if [[ "$key" == "$param" ]]; then
            echo "$val"
            exit 0
        fi
    fi

    # 情况2: --param value
    if [[ "$line" =~ --([a-zA-Z0-9._-]+)[[:space:]]+([^[:space:]]+) ]]; then
        key="${BASH_REMATCH[1]}"
        val="${BASH_REMATCH[2]}"
        if [[ "$key" == "$param" ]]; then
            echo "$val"
            exit 0
        fi
    fi
done <<< "$params"

echo "Error: Parameter '$param' not found." >&2
exit 1

```
* __scripts/spark/benchmark.sh 脚本内容：__
```YAML
cd /root/spark_auto_deploy_arm/spark_test && sh tpcds_test_1t_spark331_linearity_2p.sh
```

## 4. 执行调优程序
```bash
# 在源码根目录执行
export PYTHONPATH="`pwd`:$PYTHONPATH"
python3 src/start_tune.py
```