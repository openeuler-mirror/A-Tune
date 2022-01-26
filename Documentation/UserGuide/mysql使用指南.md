# mysql使用指南

# 环境

x86_64 + [VMWare](https://so.csdn.net/so/search?q=VMWare&spm=1001.2101.3001.7020) + openEuler 20.03 LTS SP1
root用户

# 安装MySQL

## 安装前准备

1. 停止关闭防火墙

   ```shell
   systemctl stop firewalld.service
   systemctl disable firewalld.service
   ```

   

2. 禁用SELinux

   SELinux是Linux内核中的一项安全策略，为避免MySQL使用中可能遇到的一些访问受限问题，我们将其禁用：

   ```shell
   sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
   ```

   建议禁用后重启系统。

## 安装MySQL

1. 执行以下命令，下载并安装MySQL官方的Yum Repository。

   ```shell
   wget http://dev.mysql.com/get/mysql57-community-release-el7-10.noarch.rpm
   yum -y install mysql57-community-release-el7-10.noarch.rpm
   yum -y install mysql-community-server ##如果出现GPG check FAILED，请使用yum -y install mysql-community-server --nogpgcheck 
   ```

   ![img](https://img.alicdn.com/tfs/TB1ka91h_M11u4jSZPxXXahcXXa-958-431.png)

2. 执行以下命令，启动 MySQL 数据库。

   ```
   systemctl start mysqld.service
   ```

3. 执行以下命令，查看MySQL初始密码。

   ```
   grep "password" /var/log/mysqld.log
   ```

   ![img](https://img.alicdn.com/tfs/TB1HCX6RQY2gK0jSZFgXXc5OFXa-834-36.png)

4. 执行以下命令，登录数据库。

   ```
   mysql -uroot -p
   ```

5. 执行以下命令，修改MySQL默认密码。

   ```
   set global validate_password_policy=0;  #修改密码安全策略为低（只校验密码长度，至少8位）。
   ALTER USER 'root'@'localhost' IDENTIFIED BY '12345678';
   ```

6. 执行以下命令，授予root用户远程管理权限。

   ```
   GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '12345678';
   ```

7. 输入exit退出数据库。

## 编辑engine.cnf文件

在将A-Tune运行起来后，需要编辑一下engine.cnf文件，编辑的engine.cnf文件如下：

```shell
#################################### engine ###############################
 [server]
 # the tuning optimizer host and port, start by engine.service
 # if engine_host is same as rest_host, two ports cannot be same
 # the port can be set between 0 to 65535 which not be used
 engine_host = localhost
 engine_port = 3838

 # enable engine server authentication SSL/TLS
 # default is true
 engine_tls = true
 tlsenginecacertfile = /etc/atuned/engine_certs/ca.crt
 tlsengineservercertfile = /etc/atuned/engine_certs/server.crt
 tlsengineserverkeyfile = /etc/atuned/engine_certs/server.key

 #################################### log ###############################
 [log]
 # either "debug", "info", "warn", "error", "critical", default is "info"
 level = info
 
 #################################### database ###############################
 [database]
 # enable database server
 # default is false
 db_enable = true
 
 # information about database
 # currently support for PostgreSQL database
 database = MySQL
 
 # the database service listening host and port
 db_host = localhost
 db_port = 3306
 
 # database name
 db_name = atune_db
 
 # database user info
 # user_passwd should be encrypted according to Advanced Encryption Standard (AES)
 # you can use ./tools/encrypt.py to encrypt your password
 user_name = root
 passwd_key =
 passwd_iv =
 user_passwd =
```

其中，管理数据库的参数解释如下：

- db_enable：是否启用数据库连接，默认为false，不启用。
- database：数据库名称，当前支持数据库为PostgreSQL与MySQL。
- db_host：数据库连接地址，应根据数据库的真实地址进行配置。
- db_port：数据库连接端口，应根据数据库的真实端口进行配置。
- db_name：数据库中database的名称，应根据数据库的真实信息进行配置，默认为atune_db。
- user_name：登录数据库使用的用户名，默认为admin。
- user_passwd：加密后的登录密码。
- passwd_key：加密使用的秘钥，用于对登录密码进行加解密。
- passwd_iv：偏移值，用于对登录密码进行加解密。

备注：user_passwd、passwd_key、passwd_iv均可通过运行tools/encrypt.py获取。可以使用 tools/encrypt.py   <密码>  来获取加密后的密码。