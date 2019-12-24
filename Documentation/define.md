# define<a name="ZH-CN_TOPIC_0213225905"></a>

## 功能描述<a name="section124121426195015"></a>

添加用户自定义的workload\_type，及对应的profile\_name和优化项。

## 命令格式<a name="section1019897115110"></a>

**atune-adm define**  <WORKLOAD\_TYPE\> <PROFILE\_NAME\> <PROFILE\_PATH\>

## 使用示例<a name="section5961238145111"></a>

新增一个workload type，workload type的名称为test\_type，profile name的名称为test\_name，优化项的文件路径为./example.conf

```
$ atune-adm define test_type test_name ./example.conf
```

