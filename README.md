<img src="misc/A-Tune-logo.png" width="50%" height="50%"/>

English | [简体中文](./README-zh.md)

## Introduction to A-Tune 

**A-Tune** is an OS tuning software based on AI. A-Tune uses AI technologies to enable the OS to understand services, simplify IT system optimization, and maximize optimal application performance.


I. A-Tune Installation
----------

Supported OS: openEuler 1.0 or later

### Method 1 (applicable to common users): Use the default A-Tune of openEuler.

```bash
yum install -y atune
```

### Method 2 (applicable to developers): Use the source code of the local repository for installation.

#### 1. Install dependent system software packages.
```bash
yum install -y golang-bin python3 perf sysstat hwloc-gui
```

#### 2. Install Python dependent packages.
```bash
yum install -y python3-dict2xml python3-flask-restful python3-pandas python3-scikit-optimize python3-xgboost
```
Or
```bash
pip3 install dict2xml Flask-RESTful pandas scikit-optimize xgboost
```

#### 3. Download the source code.
```bash
mkdir -p /home/gopath/src
cd /home/gopath/src
git clone https://gitee.com/openeuler/A-Tune.git atune
```

#### 4. Compile.
```bash
cd atune
export GO111MODULE=off
make
```

#### 5. Install.
```bash
make install
```

II. Quick Guide
------------

### 1. Manage the atuned service.

#### Load and start the atuned service.
```bash
systemctl daemon-reload
systemctl start atuned
```

#### Check the atuned service status.
```bash
systemctl status atuned
```

### 2. Run the atune-adm command.

#### The list command.
This command is used to list the supported workload types, profiles, and the values of Active.

Format:

atune-adm list

Example:
```bash
atune-adm list
```

#### The analysis command.
This command is used to collect real-time statistics from the system to identify and automatically optimize workload types.

Format:

atune-adm analysis [OPTIONS] [APP_NAME]

Example 1: Use the default model for classification and identification.
```bash
atune-adm analysis
```
Example 2: Use the user-defined training model for recognition.
```bash
atune-adm analysis –model ./model/new-model.m
```
Example 3: Specify the current system application as MySQL, which is for reference only.
```bash
atune-adm analysis mysql
```

For details about other commands, see the atune-adm help information or [A-Tune User Guide](./Documentation/UserGuide/UserGuide.md).
