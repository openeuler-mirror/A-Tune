# profile<a name="ZH-CN_TOPIC_0213225903"></a>

## 功能描述<a name="section124121426195015"></a>

手动激活workload\_type对应的profile，使得workload\_type处于active状态。

## 命令格式<a name="section1019897115110"></a>

**atune-adm profile **_<WORKLOAD\_TYPE\>_

## 参数说明<a name="section13406211624"></a>

_WORKLOAD\_TYPE_  支持的类型参考list命令查询结果。

## 使用示例<a name="section5961238145111"></a>

激活webserver对应的profile配置

```
$ atune-adm profile webserver
```

