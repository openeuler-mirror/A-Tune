# 采集框架开发指南

由于采集数据模块需要频繁调用shell命令，因此新增数据采集框架用于更加便捷地扩展新增采集指标，采集框架代码在src/utils目录下，下面是针对utils目录各代码文件的功能描述。

```shell
├── __init__.py
├── common.py			公共数据结构
├── json_repair.py		从大模型回复中获取json
├── llm.py			大模型统一接口调用模块
├── metrics.py			指标定义和含义
├── rag
│   ├── __init__.py			
│   └── knob_rag.py		rag检索，推荐参数模块
├── shell_execute.py		远程执行命令模块
└── thread_pool.py		线程池，用于批量并行执行任务
```



## 1.采集模块接口介绍

### SshClient接口

类定义如下：

```python
class SshClient:
    def __init__(
        self,
        host_ip: str = "",
        host_port: int = 22,
        host_user: str = "root",
        host_password: str = "",
        max_retries: int = 0,
        delay: float = 1.0,
    ):
        self.host_ip = host_ip
        self.host_port = host_port
        self.host_user = host_user
        self.host_password = host_password

        self.max_retries = max_retries
        self.delay = delay
```

| 参数名        | 参数类型 | 参数取值范围 | 参数含义说明                                       |
| ------------- | -------- | ------------ | -------------------------------------------------- |
| host_ip       | 字符串   | -            | 远程连接ssh客户端的ip                              |
| host_port     | 整型     | 0~65535      | ssh连接的端口号，一般默认是22                      |
| host_user     | 字符串   | -            | ssh连接的用户名                                    |
| host_password | 字符串   | -            | ssh连接的密码                                      |
| max_retries   | 整型     | 0~10         | 重试次数，当远程连接失败或者命令执行失败时进行重试 |
| delay         | 浮点型   | -            | 每次失败等待多久后重试                             |



执行cmd命令接口如下：

```python
def run_cmd(self, cmd: str) -> ExecuteResult:
```

| 参数名 | 参数类型 | 参数取值范围 | 参数含义说明          |
| ------ | -------- | ------------ | --------------------- |
| cmd    | 字符串   | -            | 远程连接ssh客户端的ip |



返回值为ExecuteResult类型，定义如下：

```python
class ExecuteResult:
    def __init__(self, status_code: int = -1, output: Any = None, err_msg: str = ""):
        self.status_code = status_code
        self.output = output
        self.err_msg = err_msg
```



| 参数名      | 参数类型 | 参数取值范围 | 参数含义说明          |
| ----------- | -------- | ------------ | --------------------- |
| status_code | 字符串   | -255~255     | shell命令执行结果状态 |
| output      | 任意类型 | -            | 输出结果              |
| err_msg     | 字符串   | -            | 错误信息              |



### cmd_pipeline接口

cmd_pipeline接口定义如下：

```python
def cmd_pipeline(
    cmd: str = "",
    tag: str = "default_tag",
    parallel: bool = False,
) -> ExecuteResult:
```

| 参数名      | 参数类型 | 参数取值范围 | 参数含义说明                               |
| ----------- | -------- | ------------ | ------------------------------------------ |
| status_code | 字符串   | -            | 待执行shell命令字符串                      |
| tag      | 字符串 | -            | 任务标签，用于区分任务类型，用户可自行定义 |
| parallel    | 布尔类型 | -            | 是否并行执行                               |

**cmd_pipeline**是一个修饰器，用于修饰在命令解析的函数上，使用该修饰器具备两个功能：

+ 自动执行shell命令，将shell命令结果返回给被修饰函数，在扩展数据采集接口时只需要关注如何解析输出结果即可
+ 自动注册任务，通过模块名即可获取注册的任务，便于批量提交任务到线程池执行

首先开发者需要开发一个解析命令行结果的函数，需要满足如下定义，入参output即为上方修饰器中cmd指定的shell命令输出结果，而输出类型不限定，一般设置为dict类型：

```python
@cmd_pipeline(cmd="ulimit -n", tag="static", parallel=True)
def fdlimit_parser(output: str) -> dict:
    """解析 ulimit -n 输出：文件描述符上限"""
    return {"最大文件描述符": int(output.strip())}
```

被cmd_pipeline修饰的函数会被封装成一个新的函数，入参为SshClient类型，输出为ExecuteResult类型，调用方法如下：

```python
result = fdlimit_parser(ssh_client)
```

这样就会函数原本的输出就会被封装到ExecuteResult.output中，打印result可以看到如下结果：

```shell
{'status_code': 0, 'err_msg': '', 'output': {'最大文件描述符': 1024}}
```

这样一个数据采集接口就开发完成了。



当我们在某个模块定义好了一系列的数据采集接口后，可以通过模块名获取这些接口，例如：在src.performance_collector.static_profile_collector模块定义了数据采集接口，在其他模块可以通过如下方式获取该python模块注册的所有数据采集接口：

```python
from src.performance_collector import static_profile_collector
from src.utils.shell_execute import get_registered_cmd_funcs

data_collector_funcs = get_registered_cmd_funcs(static_profile_collector)
print(data_collector_funcs)
```

这样就可以看到该模块定义的所有数据采集接口：

```shell
['func': <func lscpu_parser at 0xffffab55c2c0>, 'tag': 'static', ...]
```



## 2.并行任务调度接口

在采集数据框架中，经常会遇到某些任务需要并行执行提升采集数据效率的情况，此时可以使用并行任务调度的接口，这里并行任务也被集成到框架中可以使用，并行任务调度接口定义为：

```python
class ThreadPoolManager:
    def __init__(self, max_workers: int = 5):
```

| 参数名      | 参数类型 | 参数取值范围 | 参数含义说明       |
| ----------- | -------- | ------------ | ------------------ |
| max_workers | int      | 1-16         | 同时工作的线程数量 |

> 注意：由于python的GIL限制，多线程仅适用于IO密集型任务，若为计算密集型任务，使用并行调度不会有效，这里远程执行cmd命令也属于IO密集型任务，推荐此种情况下使用并行接口

