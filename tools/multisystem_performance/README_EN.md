# OSPP: Multiple-System Performance Verification Tool

The multi-system performance verification tool is located in the `tools` directory of A-Tune. It loads system parameters from compared systems and performs performance testing.

---

## Introduction

### Directory Structure

- `conf`: Configuration folder.
  - `config.json`: Configures the test mode and the host's `IP` and `User` information.
  - `modify.conf`: Configures the `ulimit` and `sysctl` parameters.
  - `sysctl_parameters.json`: A dictionary used for querying key-value pairs.
- `data`: Stores data processing results and performance test results.
- `log`: Log file.
- `src`: Main program.
- `tests`: Test files.
- `tools`: Third-party performance test tool.

### Supported Features

- Two test modes:
  - `communication_test`: Supports three hosts. The local host controls remote PCs (PC 1 and PC 2) to perform cross-testing.
  - `host_test`: Supports cross-testing between the local PC and remote PCs.
- Three methods for modifying parameters:
  - `copy by all`: Supports loading all parameters.
  - `copy by block`: Supports block-based import.
  - `copy by line`: Supports line-by-line modification.
- Parameter backup
- Performance testing
  - CPU, memory and drives can be tested using UnixBench.
  - The network can be tested using Netperf.
  - You can configure additional performance test commands in the `extra_benchmark` field of `modify.conf`.

### Dependencies

- `Python 3.x`
- `UnixBench`: Run `cd ./tools && git clone https://github.com/kdlucas/byte-unixbench.git` to install it.
- `nertpef`: Use the package manager to install it.

## Using the Tool

### Configuration

- Edit `/config/config.json`.
- Configure the `ulimit` and `sysctl` parameters in `modify.conf`.

### Running the Main Program in `multisystem_performance`

```python
python ./src/main.py
```

### Cleaning Log Files

```python
python ./src/clean_log.py
```

### Cleaning Data Files

```python
python ./src/clean_data.py
```

### Test

```python
pytest -p no:logging ./tests/test_***.py
```

### Viewing the Performance Test Result

- View the `UnixBench_res_output.txt` file in `data`.
