# EulerCopilot Tune安装使用指南

### 项目简介
EulerCopilot Tune通过采集系统、微架构、应用等维度的指标数据，结合大模型和定制化的prompt工程，针对不同应用的可调参数给出可靠的参数推荐，同时根据推荐的参数运行benchmark，与baseline做对比并计算出推荐参数对应用性能的提升值。

### 软件架构
软件架构说明

### 安装教程

1. 下载gitee源码，gitee代码仓地址：
https://gitee.com/openeuler/A-Tune/tree/euler-copilot-tune/
（注意：分支指定为euler-copilot-tune）
2. 安装其他依赖
```bash
#1.调优程序运行机器安装python venv依赖
yum install python3-devel krb5-devel
#2.目标应用所在机器安装调优依赖并重启sysstat
yum install sysstat perf
systemctl start sysstat
```
3. 调优程序运行机器安装python依赖:
```BASH
#1.创建并加载python venv
python3 -m venv venv
source venv/bin/activate

#2.安装python依赖包
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 使用指南

1. 准备env yaml，放入项目的config/.env.yaml中，具体格式如下：
```YAML
LLM_KEY: "YOUR_LLM_KEY"
LLM_URL: "YOUR_LLM_URL"
LLM_MODEL_NAME: "YOUR_LLM_MODEL_NAME"
LLM_MAX_TOKENS:

REMOTE_EMBEDDING_ENDPOINT: "YOUR_EMBEDDING_MODEL_URL"
REMOTE_EMBEDDING_MODEL_NAME: "YOUR_MODEL_NAME"

servers:
  - ip: ""                                                              #应用所在ip
    host_user: ""                                                       #登录机器的usr id
    password: ""                                                        #登录机器的密码
    port:                                                               #应用所在ip的具体port
    app: "mysql"                                                        #当前支持mysql、nginx、pgsql、spark
    target_process_name: "mysqld"                                       #调优应用的name
    business_context: "高并发数据库服务，CPU负载主要集中在用户态处理"           #调优应用的描述（用于策略生成）
    max_retries: 3
    delay: 1.0
    
feature:
  - need_restart_application: False                                     #修改参数之后是否需要重启应用使参数生效
    need_recover_cluster: False                                         #调优过程中是否需要恢复集群
    microDep_collector: True                                            #是否开启微架构指标踩采集
    pressure_test_mode: True                                            #是否通过压测模拟负载环境
    tune_system_param: False                                            #是否调整系统参数
    tune_app_param: True                                                #是否调整应用参数
    strategy_optimization: False                                        #是否需要策略推荐
    benchmark_timeout: 3600                                             #benchmark执行超时限制
```

2.  完善app_config.yaml，放入项目的config/app_config.yaml中（重点是补充set_param_template、get_param_template、benchmark脚本），具体内容如下：
```YAML
mysql:
  user: "root"
  password: "123456"
  config_file: "/etc/my.cnf"
  port: 3306
  set_param_template: 'grep -q "^$param_name\\s*=" "$config_file" && sed -i "s/^$param_name\\s*=.*/$param_name = $param_value/" "$config_file" || sed -i "/\\[mysqld\\]/a $param_name = $param_value" "$config_file"'
  get_param_template: 'grep -E "^$param_name\s*=" $config_file | cut -d= -f2- | xargs'
  stop_workload: "systemctl stop mysqld"
  start_workload: "systemctl start mysqld"
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/mysql/parse_benchmark.sh $host_ip $port $user $password"
  performance_metric: "QPS"

flink:
  set_param_template: 'sh /home/wsy/set_param.sh $param_name $param_value'
  get_param_template: 'sh /home/wsy/get_param.sh $param_name'
  benchmark: "sh /home/wsy/nexmark_test.sh"
  stop_workload: 'docker exec -i flink_jm_8c32g bash -c "source /etc/profile && /usr/local/flink-1.16.3/bin/stop-cluster.sh && /usr/local/nexmark/bin/shutdown_cluster.sh"'
  start_workload: 'docker exec -i flink_jm_8c32g bash -c "source /etc/profile && /usr/local/flink-1.16.3/bin/start-cluster.sh"'
  performance_metric: "THROUGHPUT"

pgsql:
  user: "postgres"
  password: "postgres"
  config_file: "/data/data1/pgsql/postgresql.conf"
  port: 5432
  set_param_template: 'grep -qE "^\s*$param_name\s*=" "$config_file" && sed -i "s/^[[:space:]]*$param_name[[:space:]]*=.*/$param_name = $param_value/" "$config_file" || echo "$param_name = $param_value" >> "$config_file"'
  get_param_template: 'grep -oP "^\s*$param_name\s*=\s*\K.*" "$config_file"'
  stop_workload: "su - postgres -c '/usr/local/pgsql/bin/pg_ctl stop -D /data/data1/pgsql/ -m fast'"
  start_workload: "su - postgres -c '/usr/local/pgsql/bin/pg_ctl start -D /data/data1/pgsql/ -l /var/log/postgresql/postgresql.log'"
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/postgresql/parse_benchmark.sh $host_ip $port $user $password"
  performance_metric: "QPS"

spark:
  set_param_template: 'sh /path/of/set_param.sh $param_name $param_value'
  get_param_template: 'sh /path/of/get_param.sh $param_name'
  benchmark: "sh /path/of/spark_benchmark.sh"
  performance_metric: "DURATION"

nginx:
  port: 10000
  config_file: "/usr/local/nginx/conf/nginx.conf"
  set_param_template: 'grep -q "^\\s*$param_name\\s\\+" "$config_file" && sed -i "s|^\\s*$param_name\\s\\+.*|    $param_name $param_value;|" "$config_file" || sed -i "/http\\s*{/a\    $param_name $param_value;" "$config_file"'
  get_param_template: 'grep -E "^\\s*$param_name\\s+" $config_file | head -1 | sed -E "s/^\\s*$param_name\\s+(.*);/\\1/"'
  stop_workload: "/usr/local/nginx/sbin/nginx -s reload"
  start_workload: "/usr/local/nginx/sbin/nginx -s reload"
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/nginx/parse_benchmark.sh $host_ip $port"
  performance_metric: "QPS"

ceph:
  set_param_template: 'ceph config set osd "$param_name" "$param_value"'
  get_param_template: 'sh /path/of/get_params.sh'
  start_workload: "sh /path/of/restart_ceph.sh"
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/ceph/parse_benchmark.sh"
  performance_metric: "BANDWIDTH"

gaussdb:
  user: ""
  password: ""
  config_file: "/path/of/config_file"
  port: 5432
  set_param_template: 'gs_guc set -Z datanode  -N all -I all -c "${param_name}=${param_value}"'
  get_param_template: 'gs_guc check -Z datanode -N all -I all -c "${param_name}"'
  stop_workload: "cm_ctl stop -m i"
  start_workload: "cm_ctl start"
  recover_workload: "$EXECUTE_MODE:local sh /path/of/gaussdb_cluster_recover.sh"
  benchmark: "$EXECUTE_MODE:local sh/path/of/gaussdb_benchmark.sh"
  performance_metric: "DURATION"

system:
  set_param_template: 'sysctl -w $param_name=$param_value'
  get_param_template: 'sysctl $param_name'

redis:
  port: 6379
  config_file: "/etc/redis.conf"
  set_param_template: "sed -i 's/^$param_name/$param_name $param_value/g' $config_file"
  get_param_template: "grep -P '$param_name' $config_file | awk '{print $2}"
  start_workload: "systemctl start redis"
  stop_workload: "systemctl stop redis"
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/redis/parse_benchmark.sh $host_ip $port "
  performance_metric: "QPS"


```
其中：
set_param_template:根据调优结果修改应用参数，用于后续测试效果
get_param_template:获取应用参数
recover_workload: 恢复集群
benchmark:benchmark脚本，格式如下：

```bash
#（必须有）用于通知框架可以执行指标采集的标识
echo 1 > /tmp/euler-copilot-fifo  

#benchmark具体执行
cd /root/spark_auto_deploy_arm/spark_test
sh tpcds_test_1t_spark331_linearity_2p.sh > /home/cxm/spark_benchmark.log 2>&1

#（必须有）计算并输出相应的performance_metric的语句
cd /home/cxm
time_taken=$(grep "time_taken:" "spark_benchmark.log" | sed -E 's/.*time_taken:([0-9.]+)s.*/\1/' | paste -sd+ | bc | xargs printf "%.2f")
echo $time_taken
```
3. 运行EulerCopilot
```bash
export PYTHONPATH="`pwd`:$PYTHONPATH"
python3 src/start_tune.py

```
#### 服务的方式运行：

1、安装服务

​		进入项目目录，执行python setup.py install 

2、在/etc/euler-copilot-tune 目录修改配置文件，具体内容参考上面源码部署方式

3、启动服务

~~~bash
#命令行执行如下命令
#开启调优
euler-copilot-tune
#开启mcpserver 日志通过执行 journalctl -xe -u tune-mcpserver --all -f 查看
tune-mcpserver
~~~

​		

### 常见问题解决

见 [FAQ.md](./FAQ.md)