# OSPP:多系统交叉验证性能工具

多系统交叉验证性能工具位于A-Tun的 tools 目录下,实现了载入对比系统的系统参数与进行性能测试的功能.

---

## 介绍

### 目录结构

- `conf` 配置文件夹
  - `config.json` 配置: 测试模式、主机的 `IP` 与 `User` 等信息
  - `modify.conf` 配置: 需要修改的`ulimit` 与 `sysctl` 参数
  - `sysctl_parameters.json` 用于查询键值的字典
- `data` 存储数据处理结果、性能测试结果
- `log` 日志文件
- `src` 主程序
- `tests` 测试文件
- `tools` 第三方性能测试工具

### 支持特性

- 2 种测试模式:
  - `communication_test` 支持 3 台主机, 本机控制远程 PC1 与 PC2 进行交叉测试
  - `host_test` 支持本机与远程 PC 进行交叉测试
- 3 种参数修改方式:
  - `copy by all` 支持载入全部参数
  - `copy by block` 支持分块导入
  - `copy by line` 支持按行修改
- 参数备份功能
- 性能测试
  - `CPU, Memory and Disk` 使用 `UnixBench` 进行测试``
  - `Network` 使用 `netperf` 进行测试
  - 可以在 `modify.conf` 的 `extra_benchmark` 配置额外的性能测试命令

### 依赖

- `Python 3.x`
- `UnixBench` 安装命令: `cd ./tools && git clone https://github.com/kdlucas/byte-unixbench.git`
- `nertpef`: 使用包管理器进行安装



## 运行方法

### 配置

- 编辑 `/config/config.json`
- 在`modify.conf` 配置需要修改的`ulimit` 与 `sysctl` 参数

### 在`multisysttem_performance`下运行主程序

```python
python ./src/main.py
```

### 清理日志文件

```python
python ./src/clean_log.py
```

### 清理数据文件

```
python ./src/clean_data.py
```
### 测试

```
pytest -p no:logging ./tests/test_***.py
```

### 查看性能测试结果

- 位于 `data` 下的 `UnixBench_res_output.txt` 文件

