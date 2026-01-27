# MySQL 安装与配置
## 1. 安装 MySQL 数据库

### yum安装（推荐）
```bash
yum install -y mysql mysql-server
```

### 源码编译
```bash
VERSION="8.0.22"
DIR="/usr/local/mysql"
DATA="/data/mysql"

# 安装依赖
dnf install -y cmake3 gcc-c++ ncurses-devel openssl-devel bison wget tar make libtirpc-devel rpcgen

# 下载源码
cd /tmp
wget -O mysql-boost.tar.gz "https://downloads.mysql.com/archives/get/p/23/file/mysql-boost-${VERSION}.tar.gz"

# 创建用户和目录
groupadd mysql 2>/dev/null || true
useradd -r -g mysql -s /bin/false mysql 2>/dev/null || true
mkdir -p ${DIR} ${DATA}
chown -R mysql:mysql ${DIR} ${DATA}

# 解压和编译
tar -xzf mysql-boost.tar.gz
cd mysql-${VERSION}
mkdir build && cd build
cmake3 .. -DCMAKE_INSTALL_PREFIX=${DIR} -DMYSQL_DATADIR=${DATA} -DWITH_BOOST=../boost -DWITH_SSL=system
make -j$(nproc) && make install
chown -R mysql:mysql ${DIR} ${DATA}

# 初始化
cd ${DIR}
bin/mysqld --initialize-insecure --user=mysql --basedir=${DIR} --datadir=${DATA}

# 创建服务
cat > /etc/systemd/system/mysqld.service <<EOF
[Unit]
Description=MySQL Server
After=network.target
[Service]
User=mysql
ExecStart=${DIR}/bin/mysqld --daemonize
ExecStop=${DIR}/bin/mysqladmin shutdown
[Install]
WantedBy=multi-user.target
EOF

# 启动服务
systemctl daemon-reload
systemctl start mysqld

# 设置密码
# ${DIR}/bin/mysqladmin -u root password "123456"
```

## 2. 启动 MySQL

```bash
systemctl start mysqld
```

## 3. 账号设置 & 创建数据库

```bash
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

# Sysbench 安装与基线测试
## 1. 安装

### yum安装（推荐）
```BASH
yum install -y sysbench
```

### 源码编译安装

```bash
yum install -y git mysql-devel automake libtool
git clone --depth=1 https://github.com/akopytov/sysbench.git
cd sysbench
./autogen.sh
./configure
make -j
make install
```

## 2. 基线测试命令

```bash
sh benchmark.sh
```

benchmark.sh 内容:

```bash
host=127.0.0.1
port=3306
user=root
passwd=123456

[[ -n "$1" ]] && host=$1
[[ -n "$2" ]] && port=$2
[[ -n "$3" ]] && user=$3
[[ -n "$4" ]] && passwd=$4

# cleanup
sysbench --db-driver=mysql --mysql-host=$host --mysql-port=$port --mysql-user=$user --mysql-password=$passwd --mysql-db=sbtest --table_size=10000 --tables=10 --time=180 --threads=16 --report-interval=5 oltp_read_write cleanup
# prepare
sysbench --db-driver=mysql --mysql-host=$host --mysql-port=$port --mysql-user=$user --mysql-password=$passwd --mysql-db=sbtest --table_size=10000 --tables=10 --time=180 --threads=16 --report-interval=5 oltp_read_write prepare
# send start signal to copilot
echo 1 > /tmp/euler-copilot-fifo
# run
sysbench --db-driver=mysql --mysql-host=$host --mysql-port=$port --mysql-user=$user --mysql-password=$passwd --mysql-db=sbtest --table-size=10000 --tables=10 --time=180 --threads=16 --report-interval=5 oltp_write_only --events=0 --mysql-storage-engine=innodb --mysql-ignore-errors=1062,1213,1205,1020 --rand-type=uniform --percentile=95 --forced-shutdown=off --db-ps-mode=disable run
# cleanup
sysbench --db-driver=mysql --mysql-host=$host --mysql-port=$port --mysql-user=$user --mysql-password=$passwd --mysql-db=sbtest --table_size=10000 --tables=10 --time=180 --threads=16 --report-interval=5 oltp_read_write cleanup
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