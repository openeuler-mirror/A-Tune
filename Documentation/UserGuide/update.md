# update<a name="ZH-CN_TOPIC_0213225906"></a>

## 功能描述<a name="section124121426195015"></a>

将workload\_type原来的优化项更新为new.conf中的内容。

## 命令格式<a name="section1019897115110"></a>

**atune-adm update**  <WORKLOAD\_TYPE\> <PROFILE\_NAME\> <PROFILE\_FILE\>

## 使用示例<a name="section5961238145111"></a>

更新负载类型为test\_type，优化项名称为test\_name的优化项为new.conf。

```
$ atune-adm update test_type test_name ./new.conf
```

