# A-Tune介绍

A-Tune是一款系统自优化的系统基础软件，该软件能够自动识别系统的负载类型，实现业务模型到资源模型的动态调度，充分发挥鲲鹏服务器的计算能力。

## 编译环境准备

第一步：**下载Go发行版**

下载链接：https://golang.org/

第二步：**现有目标环境清理**

这步，如果原有环境已经安装过go版本，要先卸载，卸载方法如下：

卸载就是清理

[root@localhost atune]# whereis go

[root@localhost atune]# whereis golang  

[root@localhost atune]# whereis gocode #如果需要的话

//找到后删除

rm -rf  xxx

第三步：**安装Go发行版**
tar -C /usr/local -xzf go-xxxxxxxxx.tar.gz 

解压后在目录 /usr/local/go中

第四步：**设置Go环境**

设置GOPATH 目录 

mkdir -p /home/gocode

编辑环境 
vim /etc/profile 
在最后一行加入 安i插入

export GOROOT=/usr/local/go #设置为go安装的路径

export GOPATH=/home/gocode  #默认安装包的路径

export PATH=$PATH:$GOROOT/bin:$GOPATH/bin

执行下面生效配置
source /etc/profile

验证是否生效
go version
输出 go version go1.11 linux/amd64


第五步：**解决protoc和protoc-gen-go三方包依赖**

1、下载protobuf源码：https://github.com/golang/protobuf

2、执行make install

3、把生成的protoc和proto-gen-go的二进制所在路径设置到系统PATH上：export PATH=$PATH:/XX/

第六步：**编译atune源码**

执行make all即可

