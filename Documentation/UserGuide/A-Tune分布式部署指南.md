# 分节点部署

### 分节点部署目的
为了实现分布式架构和按需部署的目标，A-Tune支持分节点部署。可以将三个组件分开部署，轻量化组件部署对业务影响小，也避免安装过多依赖软件，减轻系统负担。<br/>

部署方式：本文档只介绍常用的一种部署方式：在同一节点部署客户端和服务端，在另一个节点上部署引擎模块。其他的部署方式请咨询A-Tune开发人员。

**部署关系图：** <br/>
![输入图片说明](figures/Picture1.png)

### 配置文件
分节点部署需要修改配置文件，将引擎的ip地址和端口号写入配置文件中，别的组件才能访问该ip地址上的引擎组件。

1.	修改服务端节点上的`/etc/atuned/atuned.cnf`文件：<br/>
34行的`engine_host`和`engine_port`修改为引擎节点的ip地址和端口号。如上图，应该修改为`engine_host = 2.2.2.2  engine_port = 3838`<br/>
将49行和55行的 rest_tls 和engine_tls 改为false，否则需要申请和配置证书。在测试环境中可以不用配置ssl证书，但是正式的现网环境需要配置证书，否则会有安全隐患。
2.	修改引擎节点/etc/atuned/engine.cnf文件：<br/>
17行和18行的`engine_host`和`engine_port`修改为引擎节点的ip地址和端口号。如上图，应该修改为`engine_host = 2.2.2.2  engine_port = 3838`<br/>
第22行的engine_tls的值改成false。 
3.	修改完配置文件后需要重启服务，配置才会生效<br/>
服务端节点输入命令：`systemctl restart atuned`<br/>
引擎端节点输入命令：`systemctl restart atune-engine`<br/>
4.	（可选步骤）在`A-Tune/examples/tuning/compress`文件夹下运行tuning命令：<br/>
请先参考`A-Tune/examples/tuning/compress/README`的指导进行预处理<br/>
执行`atune-adm tuning --project compress --detail compress_client.yaml`<br/>
本步骤的目的是检验分节点部署是否成功。<br/>

### 注意事项
1.	本文档不对认证证书配置方法作详细说明，如有需要也可以将atuned.cnf和engine.cnf中的rest_tls/engine_tls设成false
2.	修改完配置文件后需要重启服务，否则修改不会生效
3.	注意使用atune服务时不要同时打开代理
4.	atuned.cnf 文件中的[system]模块的disk和network项需要修改，修改方法见[A-Tune用户指南2.4.1章节](https://gitee.com/gaoruoshu/A-Tune/blob/master/Documentation/UserGuide/A-Tune%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97.md)，本文不展开描述。

### 举例
#### atuned.cnf
 ![输入图片说明](figures/Picture2.png)
#### engine.cnf
 ![输入图片说明](figures/Picture3.png)

# 集群部署

### 集群部署的目的
为了支持多节点场景快速调优，A-Tune支持对多个节点里的参数配置同时进行动态调优，避免用户单独多次对每个节点进行调优，从而提升调优效率。<br/>
集群部署的方式：分为一个主节点和若干个从节点。在主节点部署客户端和服务端，负责接受命令和引擎交互。其他节点接受主节点的指令，对当前节点的参数进行配置。

**部署关系图：** <br/>
 ![输入图片说明](figures/Picture4.png)

上图中客户端和服务端部署在ip为2.2.2.1的节点上，项目文件存放在该节点上，其他节点不用放置项目文件。<br/>
主节点和从节点之间通过tcp协议通信，所以需要修改配置文件。

### atuned.cnf配置文件修改
1.	protocol 值设置为tcp
2.	address设置为当前节点的ip地址
3.	connect设置为所有节点的ip地址，第一个为主节点，其余为从节点ip，中间用逗号隔开。
4.	在调试时，可以设置rest_tls 和engine_tls 为false
所有的主从节点的atuned.cnf都按照上方描述修改

### 注意事项
1.	将engine.cnf中的`engine_host`和`engine_port`设置为服务端atuned.cnf中`engine_host`和`engine_port`一样的ip和端口号。
2.	本文档不对认证证书配置方法作详细说明，如有需要也可以将atuned.cnf和engine.cnf中的rest_tls和engine_tls设置为false
3.	修改完配置文件后需要重启服务，否则修改不会生效
4.	注意使用atune服务时不要同时打开代理

### 举例
#### atuned.cnf
![输入图片说明](figures/Picture5.png) 
#### engine.cnf
![输入图片说明](figures/Picture6.png)

**备注：** engine.cnf参考分节点部署的配置文件
