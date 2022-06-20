<img src="misc/A-Tune-logo.png" width="50%" height="50%"/>

[English](./README.md) | 简体中文

## A-Tune介绍

A-Tune是一款基于AI的操作系统性能调优引擎。A-Tune利用AI技术，使操作系统“懂”业务，简化IT系统调优工作的同时，让应用程序发挥出色性能。


一、安装A-Tune
----------

支持操作系统：openEuler 20.03 LTS及以上版本

### 方法一（适用于普通用户）：使用openEuler默认自带的A-Tune

```bash
yum install -y atune
```
#### openEuler 20.09及以上版本还需安装atune-engine

```bash
yum install -y atune-engine
```

**注：** 直接安装后尝试执行`systemctl start atuned`会出现报错信息，原因是未配置认证证书，解决方法如下：
1. 配置证书，使用https安全连接
 - 生成服务端和客户端的证书文件，并
 - 修改`/etc/atuned/atuned.cnf`中的60 ~ 62行、67 ~ 69行为证书文件的绝对路径，同时
 - 修改`/etc/atuned/engine.cnf`中的23 ~ 25行为证书的绝对路径
 - 相关证书生成方式可参考代码仓中`Makefile`文件的"restcerts"和"enginecerts"
2. 取消证书认证，使用http非安全连接
 - 在安全要求不高的场景下（如本地测试使用等），可以通过使用http连接规避该问题
 - 修改`/etc/atuned/atuned.cnf`中的rest_tls(L59)和engine_tls(L66)为false
 - 修改`/etc/atuned/engine.cnf`中的engine_tls(L22)为false
<br>
无论使用1/2哪种方法，在设置完成后均需要重启服务，具体操作方法详见"二、快速使用指南 - 2、管理A-Tune服务 - 加载并启动atuned和atune-engine服务"

### 方法二（适用于开发者）：从本仓库源码安装

#### 1、安装依赖系统软件包
```bash
yum install -y golang-bin python3 perf sysstat hwloc-gui lshw
```

#### 2、安装python依赖包  

#### 2.1 安装A-Tune服务的依赖包
```bash
yum install -y python3-dict2xml python3-flask-restful python3-pandas python3-scikit-optimize python3-xgboost python3-pyyaml
```
或
```bash
pip3 install dict2xml Flask-RESTful pandas scikit-optimize xgboost scikit-learn pyyaml
```
#### 2.2、安装数据库依赖包（可选）
如用户已安装数据库应用，并需要将A-Tune的采集和调优数据存储到数据库中，可以安装以下依赖包：
```bash
yum install -y python3-sqlalchemy python3-cryptography
```
或
```bash
pip3 install sqlalchemy cryptography
```
同时，请参照下表，根据对应的数据库应用任选一种方式进行依赖安装。
| **数据库** | **yum安装** | **pip安装** |
| ------------------------------ | ---------- | ------------ |
| PostgreSQL | yum install -y python3-psycopg2 | pip3 install psycopg2 |

#### 3、下载源码
```bash
git clone https://gitee.com/openeuler/A-Tune.git
```

#### 4、编译
```bash
cd A-Tune
make
```

#### 5、安装
```bash
make collector-install
make install
```

二、快速使用指南
------------

### 1、配置A-Tune服务

#### 修改atuned.cnf配置文件中网卡和磁盘的信息

注：如果通过'make install'安装了atuned服务，网卡和磁盘已经自动更新为当前机器中的默认设备。如果需要从其他设备收集数据，请按照以下步骤配置 atuned 服务。

通过以下命令可以查找当前需要采集或者执行网卡相关优化时需要指定的网卡，并修改/etc/atuned/atuned.cnf中的network配置选项为对应的指定网卡。

```shell
ip addr
```

通过以下命令可以查找当前需要采集或者执行磁盘相关优化时需要指定的磁盘，并修改/etc/atuned/atuned.cnf中的disk配置选项为对应的指定磁盘。

```shell
fdisk -l | grep dev
```

### 2、管理A-Tune服务

#### 加载并启动atuned和atune-engine服务

```bash
systemctl daemon-reload
systemctl start atuned
systemctl start atune-engine
```

#### 查看atuned或atune-engine服务状态

```bash
systemctl status atuned
systemctl status atune-engine
```

### 3、生成AI模型

用户可以将新采集的数据存放到A-Tune/analysis/dataset目录下，并通过执行模型生成工具，更新A-Tune/analysis/models目录下的AI模型。

接口语法：

python3 generate_models.py <OPTIONS>

参数说明

- OPTIONS

| 参数             | 描述                                                         |
| ---------------- | ------------------------------------------------------------ |
| --csv_path, -d   | 存放模型训练所需的csv文件目录，默认为A-Tune/analysis/dataset目录 |
| --model_path, -m | 训练生成的新模型存放路径，默认为A-Tune/analysis/models目录   |
| --select, -s     | 是否生成特征模型，默认为否                                   |
| --search, -g     | 是否启用参数空间搜索，默认为否                               |

运行示例：

```
python3 generate_models.py
```

### 4、atune-adm命令

#### list命令
列出系统当前支持的profile，以及当前处于active状态的profile。

接口语法：

atune-adm list

运行示例：

```bash
atune-adm list
```

#### profile命令

激活profile，使其处于active状态。

接口语法：

atune-adm profile <PROFILE>

运行示例：激活web-nginx-http-long-connection对应的profile配置

```bash
atune-adm profile web-nginx-http-long-connection
```

#### analysis命令（在线静态调优）

实时采集系统的信息进行负载类型的识别，并自动执行对应的优化。

注：analysis命令采集的部分数据来源是 atuned 服务配置文件(/etc/atuned/atuned.cnf) 中配置的硬盘和网卡，执行命令前先检查其中的配置项是否符合预期，若需从其他网卡或硬盘采集数据，则需更新 atuned 服务配置文件，并重启 atuned 服务。

接口语法：

atune-adm analysis [OPTIONS]

运行示例1：使用默认的模型进行应用识别，并进行自动优化

```bash
atune-adm analysis
```

运行示例2：使用自定义训练的模型进行应用识别

```bash
atune-adm analysis --model /usr/libexec/atuned/analysis/models/new-model.m
```

#### tuning命令（离线动态调优）

使用指定的项目文件对所选参数进行动态空间的搜索，找到当前环境配置下的最优解。

接口语法：

atune-adm tuning [OPTIONS] <PROJECT_YAML>

运行示例：参考[A-Tune 离线调优示例](./examples/tuning)，每一个示例中可参考对应的README指导文档。

其他命令使用详见atune-adm help信息或[A-Tune用户指南](./Documentation/UserGuide/A-Tune用户指南.md)。

三、webUI
----------

[A-Tune-UI](https://gitee.com/openeuler/A-Tune-UI)是基于A-Tune的前端页面，具体配置及使用方法请参考A-Tune-UI项目的[README](https://gitee.com/openeuler/A-Tune-UI/blob/master/README.md)文件。

四、如何贡献
----------
我们非常欢迎新贡献者加入到项目中来，也非常高兴能为新加入贡献者提供指导和帮助。在您贡献代码前，需要先签署[CLA](https://openeuler.org/en/cla.html)。

### 邮件列表
如果您有任何疑问或讨论，请通过[A-Tune](https://mailweb.openeuler.org/postorius/lists/a-tune.openeuler.org/)邮件列表和我们进行联系。

### 会议
每双周周五上午10:00-12:00召开SIG组例会。您可以通过[A-Tune](https://mailweb.openeuler.org/postorius/lists/a-tune.openeuler.org/)邮件列表方式申报议题。
