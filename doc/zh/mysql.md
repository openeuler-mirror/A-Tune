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
ssh -q root@9.82.245.67 "sysbench \
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
        prepare"


# 2.copilot调优信号发送
echo "发送调优信号1"
echo 1 > /tmp/euler-copilot-fifo


# 3.sysbench压测开始
echo "压测开始"
rm -rf benchmark.log

ssh -q root@9.82.245.67 "sysbench \
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
  run" 2>&1 | tee benchmark.log

# 4.sysbench清理工作
echo "开始清理工作"
ssh -q root@9.82.245.67 "sysbench \
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
 cleanup"

```