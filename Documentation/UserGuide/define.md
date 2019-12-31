# define<a name="ZH-CN_TOPIC_0213225905"></a>

## 功能描述<a name="section124121426195015"></a>

添加用户自定义的workload\_type，及对应的profile优化项。

## 命令格式<a name="section1019897115110"></a>

**atune-adm define**  <WORKLOAD\_TYPE\> <PROFILE\_NAME\> <PROFILE\_PATH\>

## 使用示例<a name="section5961238145111"></a>

新增一个workload type，workload type的名称为test\_type，profile name的名称为test\_name，优化项的配置文件为example.conf。

```
$ atune-adm define test_type test_name ./example.conf
```

example.conf 可以参考如下方式书写（以下各优化项非必填，仅供参考），也可通过**atune-adm info**查看已有的profile是如何书写的。

```
[main]
# list it's parent profile
[tip]
# the recommended optimization, which should be performed manunaly
[check]
# check the environment
[affinity.irq]
# to change the affinity of irqs
[affinity.task]
# to change the affinity of tasks
[bios]
# to change the bios config
[bootloader.grub2]
# to change the grub2 config
[kernel_config]
# to change the kernel config
[script]
# the script extention of cpi
[sysctl]
# to change the /proc/sys/* config
[sysfs]
# to change the /sys/* config
[systemctl]
# to change the system service config
[ulimit]
# to change the resources limit of user
```

