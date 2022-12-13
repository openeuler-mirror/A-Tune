### 1. 新特性开发

- 采集模块命令行工具支持界面可视化，实现轻量级的数据监控
- 支持更多采集命令，增加瓶颈点分析能力
- 实现WebUI安全认证与鉴权，发布release版本
- 引入强化学习算法模型
- 实现A-Tune并行调优的能力
- [server.yml里的调优配置项不支持两个参数相互关联](https://gitee.com/openeuler/A-Tune/issues/I59JMY?from=project-issue)
- [A-Tune 异构服务器调优 - 不同操作系统](https://gitee.com/openeuler/A-Tune/issues/I52T1C?from=project-issue)
- [贝叶斯调优算法越来越慢](https://gitee.com/openeuler/A-Tune/issues/I1O28D?from=project-issue)

### 2. 待调优的场景

- opengauss
- 国产数据库
- tomcat
- kafka
- memcached
- hive
- hbase
- storm
- 针对现有场景，获取在kvm、docker中的优化点

### 3. 待优化的数据采集工具

不同版本的采集命令存在采集项的变化，采集工具需要兼容不同版本的采集命令

### 4. 待适配的其他OS

- centos
- suse
- ubuntu

### 5. 待增加的调优算法

- 深度神经网络
- LSTM
- 强化学习

### 6. 待优化功能

- [参数调优空间映射](https://gitee.com/openEuler/A-Tune/issues/I5VWMY?from=project-issue)
- [解耦github.com/newm4n/grool软件包](https://gitee.com/openeuler/A-Tune/issues/I5QBGZ?from=project-issue)
- [A-Tune以及相关依赖包一起打包成二进制，并且可以对单独的配置文件进行配置](https://gitee.com/openeuler/A-Tune/issues/I58P0H?from=project-issue)
- [benchmark运行结果中如果有性能指标为0，则会出现调优中断](https://gitee.com/openeuler/A-Tune/issues/I3EUWW?from=project-issue)
- [The performance growth rate during incremental optimization is incorrect.](https://gitee.com/openeuler/A-Tune/issues/I1WYC0?from=project-issue)

