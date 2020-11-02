<img src="misc/A-Tune-logo.png" width="50%" height="50%"/>

[English](./README.md) | 简体中文

## A-Tune介绍

A-Tune是一款基于AI的操作系统性能调优引擎。A-Tune利用AI技术，使操作系统“懂”业务，简化IT系统调优工作的同时，让应用程序发挥出色性能。


一、安装A-Tune
----------

支持操作系统：openEuler 1.0及以上版本

### 方法一（适用于普通用户）：使用openEuler默认自带的A-Tune

```bash
yum install -y atune
```
#### openEuler 20.09及以上版本还需安装atune-engine

```bash
yum install -y atune-engine
```

### 方法二（适用于开发者）：从本仓库源码安装

#### 1、安装依赖系统软件包
```bash
yum install -y golang-bin python3 perf sysstat hwloc-gui
```

#### 2、安装python依赖包
```bash
yum install -y python3-dict2xml python3-flask-restful python3-pandas python3-scikit-optimize python3-xgboost
```
或
```bash
pip3 install dict2xml Flask-RESTful pandas scikit-optimize xgboost scikit-learn
```

#### 3、下载源码
```bash
git clone https://gitee.com/openeuler/A-Tune.git
```

#### 4、编译
```bash
cd A-Tune
make models
make
```

#### 5、安装
```bash
make install
```

二、快速使用指南
------------

### 1、管理atuned服务

#### 加载并启动atuned服务
```bash
systemctl daemon-reload
systemctl start atuned
systemctl start atune-engine
```

#### 查看atuned服务状态
```bash
systemctl status atuned
```

### 2、atune-adm命令

#### list命令
列出系统当前支持的workload类型和对应的profile，当前处于active状态的workload类型。

接口语法：

atune-adm list

示例：
```bash
atune-adm list
```

#### analysis命令
实时采集系统的信息进行负载类型的识别，并自动执行对应的优化。

接口语法：

atune-adm analysis [OPTIONS] [APP_NAME]

运行示例1：使用默认的模型进行分类识别
```bash
atune-adm analysis
```
运行示例2：使用自定义训练的模型进行识别
```bash
atune-adm analysis –model ./model/new-model.m
```
运行示例3：指定当前的系统应用为mysql，仅作为参考。
```bash
atune-adm analysis mysql
```

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
