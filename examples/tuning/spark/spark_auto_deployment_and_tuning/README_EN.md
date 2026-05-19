# Automated Deployment of Spark and HiBench Performance Benchmarking

## **Workflow**

**I. Automatic deployment of Spark**

1. Install `gcc make curl wget samba git`.
2. Disable the firewall and start `nmbd.service`.
3. Enable password-free login on the local host.
4. Install Java and configure the Java environment.
5. Install Hadoop, configure the Hadoop environment, format NameNode, and start HDFS and Yarn.
6. Install Spark, configure the Spark environment, and start the Spark master and worker daemons.

**II. Automatic deployment of HiBench**

1. Install Python 2.
2. Install Maven, configure Maven environment variables, and set up a Maven repository mirror.
3. Download, compile, and configure HiBench for benchmarking Spark.

**III. Benchmark execution**

1. Complete the preparation steps.
2. Run the test.

## Getting Started

**Prerequisites**

- Copy the current directory, including all files and subdirectories, to the host directory. Run the `ip addr` command to view the IP address of the local host. Run the `hostname` command to view the name of the local host. Add `ip hostname` to `/etc/hosts`, for example, `192.168.70.129 spark`.

- Disable the firewall.

  ```bash
  systemctl stop firewalld
  ```

- Update the system and install necessary dependencies.

  ```bash
  dnf update -y
  dnf install gcc make curl wget samba git atune atune-engine -y
  ```

- Start the services.

  ```bash
  systemctl start nmb
  systemctl start atuned
  systemctl start atune-engine
  ```

  **Note**: atuned and atune-engine may fail to be started. If this happens, you need to set `rest_tls` and `engine_tls` to `false` in `/etc/atuned/atuned.cnf`, set `network` to your network, and set `engine_tls` to `false` in `/etc/atuned/engine.cnf`.

- Enable password-free login.

  ```bash
  ssh-keygen -t rsa
  cat ~/.ssh/id_rsa.pub >>~/.ssh/authorized_keys
  ```

During automatic deployment, a large number of files need to be downloaded. If the installation fails due to network problems, you can configure a proxy.

```bash
# Configure Git proxy settings.
git config --global http.proxy http://ip:port
git config --global https.proxy http://ip:port

# Add the following lines to `~/.bashrc` to configure system proxy settings.
export http_proxy=http://ip:port
export https_proxy=http://ip:port
# Make the environment variables take effect.
source ~/.bashrc

#Replace "ip:port" with the actual IP addresses and port numbers.
```

### **Automatic Deployment of Spark**

Switch to the script directory, run the `chmod u+x ./install_spark.sh` command to grant the execute permission for the script, and then run the `./install_spark.sh` script. During the execution, you may need to enter the administrator password. Wait for a while until `Spark deployment success` is displayed on the terminal, indicating that the execution is successful. Run the `source ~/.bashrc` and `jps` commands to check that the running daemons are NameNode, NodeManager, SecondaryNameNode, ResourceManager, DataNode, Master, and Worker.

If the execution fails, check the `install_spark.log` file in the directory to check which step fails.

### Automatic Deployment of HiBench

Switch to the script directory, run the `chmod u+x ./install_hibench.sh` command to grant the execute permission for the script, and then run the `./install_hibench.sh` script. During the execution, you may need to enter the administrator password. Wait for a while until `Hibench init success` is displayed on the terminal, indicating that the execution is successful.

If the execution fails, check the `install_hibench.log` file in the directory to check which step fails.

### Benchmark Execution

Go to the script directory.

```bash
sh HiBench/bin/workloads/sql/join/prepare/prepare.sh
sh HiBench/bin/workloads/sql/join/spark/run.sh
# Result
cat HiBench/report/hibench.log
```

## A-Tune HiBench Performance Tuning

**Parameters of the instance machine**:

- Virtualization: VMware Workstation 17
- OS: openEuler 22.03 SP1
- CPU: AMD Ryzen 7 4800H with Radeon Graphics (2 CPUs and 4 cores)
- Memory: 8 GB
- Drives: 128 GB

**Spark tuning parameters**:

- `num_executors`: Number of executors, which ranges from 2 to 4.
- `executor_core`: Number of cores per executor, which ranges from 2 to 4.
- `executor_memory`: Executor memory, which ranges from 1 GB to 4 GB.
- `driver_memory`: Driver memory, which ranges from 1 GB to 2 GB.
- `default_parallelism`: Default degree of parallelism, which ranges from 10 to 50.
- `storageLevel`: Default storage level of resilient distributed datasets (RDDs), which ranges from 0 to 2.
- `shuffle_partition`: Number of shuffle partitions, which ranges from 1 to 4.

**Change the HDFS data scale to `huge`. For details, see "Adjusting the HiBench Test Data Scale".**

### Performing the Test

First, generate test data: `sh HiBench/bin/workloads/sql/join/prepare/prepare.sh`.

Copy `spark_hibench_server.yaml` to `/etc/atuned/tuning`.

```bash
cp spark_hibench_server.yaml /etc/atuned/tuning
# Note that all `get` and `set` paths in `spark_hibench_server.yaml` must point to the location of `spark_hibench.sh`.
```

Start performance tuning.

```bash
atune-adm tuning --project spark_hibench --detail ./spark_hibench_client.yaml
```

Note: The instance test result is saved in the `atune_spark_bench.log` file in this directory.
