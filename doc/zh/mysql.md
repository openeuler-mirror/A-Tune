# MySQL 安装与配置
## 1. 安装 MySQL 数据库

```
yum install -y mysql mysql-devel mysql-server
```
## 2. 创建运行目录

```
mkdir -p /usr/local/mysql/{data,tmp,run,log}
```

## 3. 修改目录属组

```
chown -R mysql:mysql /usr/local/mysql
```

## 4. 清理数据

```
rm -rf /usr/local/mysql/data/*
```

## 5. 将可执行文件目录加入到 PATH

```
export PATH=`echo $PATH`:/usr/local/mysql/bin
```

## 6. 初始化 MySQL 数据库

```
mysqld --user=root --initialize-insecure
```

## 7. 启动 MySQL

```
chown -R mysql:mysql /var/lib/mysql
chown -R mysql:mysql /run/mysqld/
systemctl start mysqld
```

## 8. 数据库配置修改

```
mysql -uroot << EOF
alter user 'root'@'localhost' identified by '123456';
flush privileges;
use mysql;
update user set host='%' where user='root';
flush privileges;
create database sbtest;
quit
EOF
```

## 9. 重载配置参数

```
systemctl daemon-reload
```

# Sysbench 安装与基线测试
## 1. 源码下载编译安装

```
yum install -y git
git clone --depth=1 https://github.com/akopytov/sysbench.git
cd sysbench
yum install -y automake libtool
./autogen.sh
./configure
make -j
make install
```

## 2. 查看版本

```
sysbench --version
```

## 3. 基线测试命令

```
sh -x benchmark.sh 127.0.0.1 3306 root 123456
```

## benchmark.sh 内容

```
# 1.prepare 阶段

echo "sysbench prepare"
sysbench \--db-driver=mysql \
    --mysql-host=$1 \
    --mysql-port=$2 \
    --mysql-user=$3 \
    --mysql-password=$4 \
    --mysql-db=sbtest \
    --table_size=10000 \
    --tables=10 \
    --time=180 \
    --threads=96 \
    --report-interval=10 \
    oltp_read_write \
    prepare


# 2.copilot调优信号发送
echo "发送调优信号1"
echo 1 > /tmp/euler-copilot-fifo


# 3.sysbench压测开始
echo "压测开始"
rm -rf benchmark.log

sysbench \
    --mysql-host=$1 \
    --mysql-port=$2 \
    --mysql-user=$3 \
    --mysql-password=$4 \
    --mysql-db=sbtest \
    --mysql-storage-engine=innodb \
    --mysql-ignore-errors=1062,1213,1205,1020 \
    --table-size=10000 \
    --tables=10 \
    --time=180 \
    --events=0 \
    --report-interval=1 \
    --rand-type=uniform \
    --rand-seed=100 \
    --db-driver=mysql \
    --percentile=95 \
    --forced-shutdown=off \
    --db-ps-mode=disable \
    --threads=128 \
    oltp_write_only \
    run 2>&1 | tee benchmark.log

# 4.sysbench清理工作
echo "开始清理工作"
sysbench \
    --db-driver=mysql \
    --mysql-host=$1 \
    --mysql-port=$2 \
    --mysql-user=$3 \
    --mysql-password=$4 \
    --mysql-db=sbtest \
    --table_size=10000 \
    --tables=10 \
    --time=180 \
    --threads=96 \
    --report-interval=10 \
    oltp_read_write \
    cleanup

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
    app: "mysql"                        #当前支持mysql、nginx、pgsql、spark
    target_process_name: "mysqld"       #调优应用的name
    business_context: "高并发数据库服务，CPU负载主要集中在用户态处理"    #调优应用的描述（用于策略生成）
    max_retries: 3
    delay: 1.0
```
* __应用部署信息 config/app_config.yaml 配置__        
需按实际环境填写；一般无需修改，若部署方式不同需要修改对应命令。
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
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/mysql/parse_benchmark.sh 127.0.0.1 3306 root 123456"
  performance_metric: "QPS"
```

* __scripts/mysql/benchmark.sh 脚本内容：__
```YAML
sysbench --db-driver=mysql --mysql-host=$1 --mysql-port=$2 --mysql-user=$3 --mysql-password=$4 --mysql-db=sbtest --table_size=5000 --tables=10 --time=180 --threads=96 --report-interval=10 oltp_read_write prepare
echo 1 > /tmp/euler-copilot-fifo"
sysbench --mysql-host=$1 --mysql-port=$2 --mysql-user=$3 --mysql-password=$4 --mysql-db=sbtest --mysql-storage-engine=innodb --mysql-ignore-errors=1062,1213,1205,1020 --tables=10 --table-size=5000 --time=180 --events=0 --report-interval=1 --rand-type=uniform --db-driver=mysql --percentile=95 oltp_read_write --forced-shutdown=off --db-ps-mode=disable --threads=128 run
sysbench --db-driver=mysql --mysql-host=$1 --mysql-port=$2 --mysql-user=$3 --mysql-password=$4 --mysql-db=sbtest --table_size=5000 --tables=10 --time=180 --threads=96 --report-interval=10 oltp_read_write cleanup
```

## 4. 执行调优程序
```bash
# 在源码根目录执行
export PYTHONPATH="`pwd`:$PYTHONPATH"
python3 src/start_tune.py
```