# 常见问题与解决方法

## **问题1：train命令训练模型出错，提示“training data failed”**

原因：collection命令只采集一种类型的数据。

解决方法：至少采集两种数据类型的数据进行训练。

## **问题2：atune-adm无法连接atuned服务**

可能原因：

1. 检查atuned服务是否启动，并检查atuned侦听地址。

    ```shell
    # systemctl status atuned
    # netstat -nap | grep atuned
    ```

2. 防火墙阻止了atuned的侦听端口。
3. 系统配置了http代理导致无法连接。

解决方法：

1. 如果atuned没有启动，启动该服务，参考命令如下：

    ```shell
    # systemctl start atuned
    ```

2. 分别在atuned和atune-adm的服务器上执行如下命令，允许侦听端口接收网络包，其中60001为atuned的侦听端口号。

    ```shell
    # iptables -I INPUT -p tcp --dport 60001 -j ACCEPT
    # iptables -I INPUT -p tcp --sport 60001 -j ACCEPT
    ```

3. 不影响业务的前提下删除http代理，或对侦听IP不进行http代理，命令如下：

    ```shell
    # no_proxy=$no_proxy,侦听地址
    ```

## **问题3：atuned服务无法启动，提示“Job for atuned.service failed because a timeout was exceeded.”**

原因：hosts文件中缺少localhost配置

解决方法：在/etc/hosts文件中127.0.0.1这一行添加上localhost

```conf
127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4
```
