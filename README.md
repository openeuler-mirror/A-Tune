<img src="misc/A-Tune-logo.png" width="50%" height="50%"/>

English | [简体中文](./README-zh.md)

## Introduction to A-Tune 

**A-Tune** is an OS tuning engine powered by AI. A-Tune uses AI technologies to enable the OS to understand services, simplify IT system tuning, and maximize application performance.


I. A-Tune Installation
------------

Supported OS: openEuler 20.03 LTS or later

### Method 1 (applicable to common users): Use the default A-Tune of openEuler.

```bash
yum install -y atune
```
For openEuler 20.09 or later, atune-engine is needed.

```bash
yum install -y atune-engine
```
**Note:** After running `systemctl start atuned`, an error message may displayed because of the authentication certificate is not configured. There are two ways to solve the problem:
1. Configure the certificate and use HTTPS for secure connection
 - Generate the certificate files of the server and client, then
 - Change lines 60 ~ 62 and 67 ~ 69 in `/etc/anined/anined.cnf` to the absolute path of the certificate file
 - Change lines 23 ~ 25 in `/etc/atuned/engine.cnf` to the absolute path of the certificate file
 - For details about how to generate certificates, see `restcerts` and `enginecerts` in `A-Tune/Makefile`
2. Cancel certificate authentication and use HTTP insecure connection
 - In scenarios with low security requirements (for example, local tests), you can use the HTTP connection
 - Change the values of `rest_tls(L59)` and `engine_tls(L66)` in `/etc/atuned/atuned.cnf` to false
 - Change the value of `engine_tls(L22)` in `/etc/atuned/engine.cnf` to false
<br>
No matter which method is used, one should restart services after the setting is complete. For details, see "II. Quick Guide - 2. Manage the A-Tune service - Load and start the atuned and atune-engine services".

### Method 2 (applicable to developers): Use the source code of the local repository for installation.

#### 1. Install dependent system software packages.
```bash
yum install -y golang-bin python3 perf sysstat hwloc-gui lshw
```

#### 2. Install Python dependency packages.  

#### 2.1 Install dependency for the A-Tune service.
```bash
yum install -y python3-dict2xml python3-flask-restful python3-pandas python3-scikit-optimize python3-xgboost python3-pyyaml
```
Or
```bash
pip3 install dict2xml Flask-RESTful pandas scikit-optimize xgboost scikit-learn pyyaml
```

#### 2.2 (Optional) Install dependency for the database.
If you have already installed the database application and want to store A-Tune collection and tuning data to the database, you must also install the following packages:
```bash
yum install -y python3-sqlalchemy python3-cryptography
```
Or
```bash
pip3 install sqlalchemy cryptography
```
To use the database, you should also select either of the following methods to install dependency for the database application.
| **Database** | **Install Using yum** | **Install Using pip** |
| ------------------------------ | ---------- | ------------ |
| PostgreSQL | yum install -y python3-psycopg2 | pip3 install psycopg2 |
#### 3. Download the source code.
```bash
git clone https://gitee.com/openeuler/A-Tune.git
```

#### 4. Compile.
```bash
cd A-Tune
make
```

#### 5. Install.
```bash
make collector-install
make install
```

II. Quick Guide
------------

### 1. Configure the A-Tune service.

#### Modify the network and disk configuration in the atuned.cnf file.

Note: If the atuned service is installed by 'make install', NIC and disk have been automatically updated to the default device in current machine. If you need to collect data from other devices, configure atuned service according to following step.

You can run the following command to query the NIC that needs to be specified for data collection or optimization and change the value of the network configuration item in the **/etc/atuned/atuned.cnf** file to the specified NIC.

```bash
ip addr
```

You can run the following command to query the disk that needs to be specified for data collection or optimization and change the value of the disk configuration item in the **/etc/atuned/atuned.cnf** file to the specified disk.

```bash
fdisk -l | grep dev
```

### 2. Manage the A-Tune service.

#### Load and start the atuned and atune-engine services.

```bash
systemctl daemon-reload
systemctl start atuned
systemctl start atune-engine
```

#### Check the status of the atuned and atune-engine services.

```bash
systemctl status atuned
systemctl status atune-engine
```

### 3. Generate AI models.

You can save the newly collected data to the **A-Tune/analysis/dataset** directory and run the model generation tool to update the AI model in the **A-Tune/analysis/models** directory.

**Format**

python3 generate_models.py <OPTIONS>

**Parameter Description**



| Parameter        | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| --csv_path, -d   | Path for storing CSV files required for model training. The default directory is **A-Tune/analysis/dataset**. |
| --model_path, -m | Path for storing the new models generated during training. The default path is **A-Tune/analysis/models**. |
| --select, -s     | Indicates whether to generate feature models. The default value is **false**. |
| --search, -g     | Indicates whether to enable parameter space search. The default value is **false**. |

Example:

```
python3 generate_models.py
```

### 4. Run the atune-adm commands.

#### list command

This command is used to list the supported profiles as well as active profiles.

Format:

atune-adm list

Example:

```bash
atune-adm list
```

#### profile command

This command is used to manually activate the profile to make it in the active state.

Format:

atune-adm profile <PROFILE>

Example: Activate the profile corresponding to the web-nginx-http-long-connection.

```bash
atune-adm profile web-nginx-http-long-connection
```

#### analysis command (online static tuning)

This command is used to collect real-time statistics from the system to identify and automatically optimize workload types.

Note: Some data collected by the analysis command are from the hard disk and network card configured in the atuned service configuration file (/etc/atuned/atuned.cnf). Before executing the command, check whether the configuration items are as expected. To collect data from other network cards or hard disk, you need to update the atuned service configuration file and restart the atuned service.

Format:

atune-adm analysis [OPTIONS]

Example 1: Use the default model to identify applications and perform automatic tuning.

```bash
atune-adm analysis
```

Example 2: Use the user-defined model for recognition.

```bash
atune-adm analysis --model /usr/libexec/atuned/analysis/models/new-model.m
```

#### tuning command (offline dynamic tuning)

Use the specified project file to search the dynamic space for parameters and find the optimal solution under the current environment configuration.

Format:

atune-adm tuning [OPTIONS] <PROJECT_YAML>

Example: See [the A-Tune offline tuning example](./examples/tuning). Each example has a corresponding README guide.

For details about other commands, see the atune-adm help information or [A-Tune User Guide](./Documentation/UserGuide/A-Tune-User-Guide.md).

III. Web UI
--------

[A-Tune-UI](https://gitee.com/openeuler/A-Tune-UI) is a web project based on A-Tune. Please check A-Tune-UI [README](https://gitee.com/openeuler/A-Tune-UI/blob/master/README.en.md) for details.

IV. How to Contribute
--------

We welcome new contributors to participate in the project, and we are happy to provide guidance for new contributors. Please sign [CLA](https://openeuler.org/en/cla.html) before contribution.

### Mailing list
If you have any question, please contact [A-Tune](https://mailweb.openeuler.org/postorius/lists/a-tune.openeuler.org/).

### Routine meeting
The SIG meeting is hold at 10:00-12:00 AM on Friday every two weeks. Please send your issues to the [A-Tune](https://mailweb.openeuler.org/postorius/lists/a-tune.openeuler.org/) mailing list.
