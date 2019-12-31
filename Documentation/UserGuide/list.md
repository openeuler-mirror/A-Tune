# list<a name="ZH-CN_TOPIC_0213225902"></a>

## 功能描述<a name="section124121426195015"></a>

查询系统当前支持的workload\_type和对应的profile，以及当前处于active状态的profile。

## 命令格式<a name="section1019897115110"></a>

**atune-adm list**

## 使用示例<a name="section5961238145111"></a>

```
$ atune-adm list

Support WorkloadTypes:
+-----------------------------------+------------------------+-----------+
| WorkloadType                      | ProfileName            | Active    |
+===================================+========================+===========+
| default                           | default                | true      |
+-----------------------------------+------------------------+-----------+
| webserver                         | ssl_webserver          | false     |
+-----------------------------------+------------------------+-----------+
| big_database                      | database               | false     |
+-----------------------------------+------------------------+-----------+
| big_data                          | big_data               | false     |
+-----------------------------------+------------------------+-----------+
| in-memory_computing               | in-memory_computing    | false     |
+-----------------------------------+------------------------+-----------+
| in-memory_database                | in-memory_database     | false     |
+-----------------------------------+------------------------+-----------+
| single_computer_intensive_jobs    | compute-intensive      | false     |
+-----------------------------------+------------------------+-----------+
| communication                     | rpc_communication      | false     |
+-----------------------------------+------------------------+-----------+
| idle                              | default                | false     |
+-----------------------------------+------------------------+-----------+

```

>![](public_sys-resources/icon-note.gif) **说明：**   
>Active为true表示当前激活的profile，示例表示当前激活的是default类型对应的profile。  

