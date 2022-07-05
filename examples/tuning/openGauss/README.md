1. Install openGauss according to the guide (https://opengauss.org/zh/docs/1.1.0/docs/installation/installation.html)
```bash
# install dependency
yum install -y libaio-devel flex bison ncurses-devel glibc-devel patch libnsl openeuler-lsb-core readline-devel

# download software package from official website
[[ `arch` == "x86_64" ]] && wget https://opengauss.obs.cn-south-1.myhuaweicloud.com/2.1.0/x86_openEuler/openGauss-2.1.0-openEuler-64bit.tar.bz2
[[ `arch` == "aarch64" ]] && wget https://opengauss.obs.cn-south-1.myhuaweicloud.com/2.1.0/arm/openGauss-2.1.0-openEuler-64bit.tar.bz2

# create install dir and extract files
mkdir -p /opt/software/openGauss
tar -xf openGauss-2.1.0-openEuler-64bit.tar.bz2 -C /opt/software/openGauss

# create user for opengauss usage
adduser opengauss
chown -R opengauss /opt/software/openGauss
chgrp -R opengauss /opt/software/openGauss

# run install script, with password "password@123"
su - opengauss
cd /opt/software/openGauss/simpleInstall
sh install.sh -w "password@123"

# verify install result
source ~/.bashrc
gs_ctl quary -D /opt/software/openGauss/data/single_node

# create benchmark database as tpcc
gsql -d postgres -r -c 'create database tpcc; create user tpcc with password "password@123"; grant all privileges to tpcc;'

# quit opengauss user
exit
```

2. Install benchmarksql-5.0 as benchmark
```bash
# install dependency
yum install -y java ant

# download software package and extract files
wget https://udomain.dl.sourceforge.net/project/benchmarksql/benchmarksql-5.0.zip
unzip -q benchmark-5.0.zip
cd benchmarksql-5.0

# install opengauss jdbc driver for benchmarksql
[[ `arch` == "x86_64" ]] && wget https://opengauss.obs.cn-south-1.myhuaweicloud.com/2.1.0/x86_openEuler/openGauss-2.1.0-JDBC.tar.gz
[[ `arch` == "aarch64" ]] && wget https://opengauss.obs.cn-south-1.myhuaweicloud.com/2.1.0/arm/openGauss-2.1.0-JDBC.tar.gz
tar -xvf openGauss-2.1.0-JDBC.tar.gz
rm ./lib/postgres/postgresql*.jar
mv ./postgresql.jar ./lib/postgres/gsjdbc4.jar
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:`pwd`/lib/postgres/gsjdbc4.jar
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:`pwd`/lib/postgres/gsjdbc4.jar" >> /etc/profile

# create benchmark configuration file props.opengauss
cd run/
cp props.pg props.opengauss
vim props.opengauss
```
edit as following:
```
// connection parameters
db=postgres
driver=org.postgresql.Driver
conn=jdbc:postgresql://localhost:5432/tpcc
user=tpcc
password=password@123

// number of warehouses, each warehouse contains about 80M data, total warehouses size should not exceed available memory
warehouses=20
// number of processes used to load data, should not exceed cpu core number
loadWorkers=4
// concurrent terminal count, usually not more than cpu core number
terminals=4
// To run specified transactions per terminal - runMins must equal zero
runTxnsPerTerminal=0
// To run benchmark for specified minutes - runTxnsPerTerminal must equal zero
runMins=5
// number of total transactions per minute, 0 means no limit
limitTxnsPerMin=0
// binding mode for terminal and warehouse, usually set true for TPCC
terminalWarehouseFixed=true

// comment following options
//osCollectorScript=...
//osCollectorInterval=...
//osCollectorSSHAddr=...
//osCollectorDevices=...
```

build benchmark database:
```
./runDatabaseBuild.sh props.opengauss
```

3. Prepare the environment

sh prepare.sh

4. Start to tuning

atune-adm tuning --project openGauss_tpcc --detail openGauss_client.yaml

5. Restore the environment

atune-adm tuning --restore --project openGauss_tpcc

