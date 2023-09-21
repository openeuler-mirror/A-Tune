# OSPP：多系统交叉验证性能工具U

## 文件结构

```bash
├── config
│   ├── change.json 
│   ├── config.json
│   ├── prefix.json
│   └── sysyctl_paraments.json
├── data
├── LICENSE
├── log
│   ├── get_sysctl_ulimit_2023-09-20-10-01-00.log
│   ├── load_config_2023-09-20-10-01-00.log
├── OSPP data
│   ├── systemctl@centos.txt
│   └── systemctl@openeuler.txt
├── README.md
├── src
│   ├── benchmark_test.py
│   ├── clean_data.py
│   ├── clean_log.py
│   ├── get_parameters.py
│   ├── import subprocess.py
│   ├── load_check.py
│   ├── main.py
│   ├── regex_prefix.py
│   └── set_parameters.py
├── tests
│   ├── test_benchmark_test.py
│   ├── test_get_parameters.py
│   ├── test_load_config.py
│   └── test_regex_prefix.py
└── tools
    ├── byte-unixbench
    │   ├── LICENSE.txt
    │   ├── README.md
    │   └── UnixBench
    ├── netperf
    └── requirement.txt


```

## 依赖

​	Python 3.x

​	UnixBench：CPU、内存与文件性能测试工具，安装在 /tools/ 目录下

​	netperf：网络性能测试工具，安装在 /tools/ 目录下

## 运行方法

### 	配置主机IP与用户名：编辑 /config/config.json

### 	运行主程序

```python
python ./src/main.py
```

### 	清理日志文件

```python
python ./src/clean_log.py
```

### 	清理数据文件

```
python ./src/clean_data.py
```


