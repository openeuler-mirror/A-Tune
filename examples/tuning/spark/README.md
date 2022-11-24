## Example of Spark tuning based on HiBench

**Prepare：**A-Tune environment

**Run Command：**
```bash
source run_env.sh
```

**Workflow：**
1. Configure java environment
2. Configure node information
3. Configure hadoop environment（hadoop-2.9.2）
4. Configure ssh password free login between nodes
5. Turn off the firewall
6. Synchronize cluster time
7. Write cluster distribution script
8. Initialize hadoop
9. Configure python 2.7 environment based on anaconda3（anaconda3-5.2.0）
10. Configure Spark environment（spark-2.4.0）
11. Configure scala environment（scala-2.11.0）
12. Configure maven environment（maven-3.5.4）
13. Configure HiBench environment

**Tips：**
(1) If some software packages cannot be downloaded due to network and other reasons, please install them by yourself
(2) The configuration information about hardware resources should be set according to the actual situation
(3) The software is installed in the "/apps" directory, and A-Tune is installed in the root directory

**Tip：**
The following commands in bash are executed when the run_env.sh script is running. Here is a brief description

1、Configure java environment
----------
1.1、Check java environment
1.2、Download jdk
1.3、Configure JAVA_ HOME environment variable
```bash
Do you want to configure JAVA_ HOME environment variable? ( yes | no ) : **yes**
```

2、Configure node information
----------
```bash
Please enter the number of nodes: **3**
Please enter the IP address of the master node: **192.168.52.1**
Please enter the IP of the first slave node: **192.168.52.2**
Please enter the IP of the second slave node: **192.168.52.3**
```

3、Configure hadoop environment（hadoop-2.9.2）
----------
3.1、Download hadoop
```bash
Do you want to configure hadoop environment(hadoop2.9.2)? ( yes | no ) : **yes**
```
3.2、Modify hadoop configuration files
```bash
rm：Do you want to delete ordinary file '/apps/hadoop-2.9.2.tar.gz'？**y**
```

4、Configure ssh password free login between nodes
----------
**Tip：**You need to enter the password of each node multiple times
```bash
Do you want to configure ssh password less login? ( yes | no ) : **yes**
Are you sure you want to continue connecting (yes/no/[fingerprint])? **yes**
root@localhosts password: **[password]**
Enter file in which to save the key (/root/.ssh/id_rsa): **enter**
Enter passphrase (empty for no passphrase): **enter**
Enter same passphrase again: **enter**
rm：Do you want to delete ordinary file '/root/authorized_keys_node2'？**y**
```

5、Turn off the firewall
----------

6、Synchronize cluster time
----------

7、Write cluster distribution script
----------
7.1、Write script xsync
7.2、Give permissions to xsync
7.3、Distribute xsync to other nodes
```bash
Please enter the number of nodes: **3**
Are you sure you want to continue connecting (yes/no/[fingerprint])? **yes**
```

8、Configure the java environment for the slave node
----------
```bash
Do you want to configure the java environment for the slave node? ( yes | no ) : **yes**
Please enter the number of nodes: **3**
```

9、Distribute hadoop files to slave nodes
----------
```bash
Do you want to distribute hadoop files to slave nodes? ( yes | no ) : **yes**
Please enter the number of nodes: **3**
```

10、Initialize hadoop
----------

11、Configure python 2.7 environment based on anaconda3（anaconda3-5.2.0）
----------
```bash
Do you want to install anaconda3(anaconda3-5.2.0)? ( yes | no ) : **yes**
Please, press ENTER to continue >>> **enter**
（show --more-- ，You need to press enter several times here）
Do you accept the license terms? [yes|no] [no] >>> **yes**
[/root/anaconda3] >>> **/apps/anaconda3**
Do you wish the installer to prepend the Anaconda3 install location to PATH in your /root/.bashrc ? [yes|no] [no] >>> **yes**
Proceed ([y]/n)? **y**
```

12、Configure Spark environment（spark-2.4.0）
----------
12.1、Install spark
```bash
Do you want to install Spark(spark2.4.0)? ( yes | no ) : **yes**
```
12.2、Configure Spark environment
```bash
Do you want to configure the spark environment? ( yes | no ) : **yes**
```
12.3、Distribute Sparks to Slave Nodes
```bash
Do you want to distribute spark to slave nodes(spark2.4.0)? ( yes | no ) : **yes**
Please enter the number of nodes: **3**
```

13、Configure scala environment（scala-2.11.0）
----------
```bash
Do you want to configure scala environment(scala2.11.0)? ( yes | no ) : **yes**
```

14、Configure maven environment（maven-3.5.4）
----------
```bash
Do you want to configure maven environment(maven3.5.4)? ( yes | no ) : **yes**
```

15、Configure HiBench environment
----------
15.1、Pull HiBench from github
```bash
Do you want to configure the hibench environment? ( yes | no ) : **yes**
```
15.2、Compile

**Tip：**If the error "/usr/bin/env:" python2 ": there is no such file or directory" appears, you need to execute "source activate spark" on each node to activate the python2 environment