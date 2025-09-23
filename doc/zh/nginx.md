# Nginx 应用验证

## 安装应用 & 环境准备
### 1. 安装 Nginx
* __安装依赖 & 下载 Nginx 源码__
```bash
# 安装依赖
yum install -y openssl openssl-devel pcre pcre-devel zlib zlib-devel gcc make

# 若服务器可以访问网络，通过 wget 命令直接下载 Nginx 源码，再将 Nginx 源码上传到虚拟机的“/home”目录。
wget https://nginx.org/download/nginx-1.21.5.tar.gz --no-check-certificate
```

### 2. 部署 Nginx
```bash
tar -zxvf nginx-1.21.5.tar.gz
cd nginx-1.21.5/
chmod 755 configure
./configure --prefix=/usr/local/nginx --user=nginx --group=nginx --with-http_ssl_module --with-http_v2_module --with-http_realip_module --with-http_stub_status_module --with-http_gzip_static_module --with-pcre --with-stream --with-stream_ssl_module --with-stream_realip_module
make -j 60 && make install
```

### 3. 生成 OpenSLL 证书
* __进入 "/usr/local/nginx" 目录，生成 RSA 密钥__（对于 CentOS 7.6 或 CentOS 8.1 下通过镜像站 RPM 包安装的 Nginx，目录需替换为 "/etc/nginx" ）
```bash
cd /usr/local/nginx
openssl genrsa -des3 -out server_2048.key 2048
# 此处系统会提示需要两次输入密码，请设置为相同的密码，完成后会生成 server_2048.key 文件。

# 设置完成后可通过以下命令实现免密使用 server_2048.key 文件。
openssl rsa -in server_2048.key -out server_2048.key
```
* __创建服务器证书的申请文件__    
```bash
openssl req -new -key server_2048.key -out server_2048.csr
# Country Name 填写 CN，其他选项直接回车
```
* __重写 RSA 密钥并生成证书__ 
```bash
openssl rsa -in server_2048.key -out server_2048.key
openssl x509 -req -days 365 -in server_2048.csr -signkey server_2048.key -out server_2048.crt
```
*注意：若生成 OpenSSL 证书时，提示 "unable to find 'distinguished_name' in config" ，说明与验证 KAE 性能时执行的 export OPENSSL_CONF=/home/openssl.cnf 命令冲突，请参见[部署 vKAE 特性时，在虚拟机部署 Nginx 过程中生成 OpenSSL 证书时报错](https://www.hikunpeng.com/document/detail/zh/kunpengcpfs/systuningguide/systemtg/kunpengvkae_20_022.html)解决该问题。
 
### 4. 配置使能 KAE + Nginx 的同步模式
* 对于不使能 KAE，以及使能 KAE + Nginx 的异步模式的配置详情，请参见[部署 Ngnix 指南](https://www.hikunpeng.com/document/detail/zh/kunpengcpfs/basicAccelFeatures/comAccel/kunpengvkae_20_016.html)。     
* __在“usr/local/nginx/conf”目录下创建一个名为 nginx_kae.conf 的配置文件，配置内容如下：__
```YAML
user  root;
worker_processes auto;
#4-7
#worker_cpu_affinity
#10000
#100000
#1000000
#10000000
#;
#daemon off;
error_log  /dev/null;

worker_rlimit_nofile 102400;
events {
        use epoll;
        worker_connections 102400;
        accept_mutex off;
        multi_accept on;
}

http {
        include       mime.types;
        default_type  application/octet-stream;
        #log_format  main  '$remote_addr - $remote_user [$time_local] $request_time "$request" '
        #        '$status $body_bytes_sent $request_length $bytes_sent "$http_referer" '
        #        '"$http_user_agent" "$http_x_forwarded_for"';
        #access_log  logs/access.log  main;
        access_log  off;

        sendfile      on;
        tcp_nopush    on;
        tcp_nodelay   on;
        server_tokens off;
        sendfile_max_chunk 512k;
        keepalive_timeout  65;
        keepalive_requests 20000;
        client_header_buffer_size 4k;
        large_client_header_buffers 4 32k;
        server_names_hash_bucket_size 128;
        client_max_body_size 100m;
        open_file_cache max=102400 inactive=40s;
        open_file_cache_valid 50s;
        open_file_cache_min_uses 1;
        open_file_cache_errors on;
        #gzip  on;

    server {
        listen       10000 reuseport;
        server_name  localhost;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;

        location / {
            root   html;
            index  index.html index.htm;
        }

        #error_page  404              /404.html;

        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }

    }
    # HTTPS server
    #
    server {
        listen       20000 ssl reuseport;
        server_name  localhost;

        ssl_certificate  /usr/local/nginx/server_2048.crt;
        ssl_certificate_key  /usr/local/nginx/server_2048.key;

        ssl_session_cache    shared:SSL:1m;
        ssl_session_timeout  5m;
        ssl_protocols  TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers  AES256-GCM-SHA384;
        ssl_prefer_server_ciphers  on;
        ssl_session_tickets  off;
        location / {
            root   html;
            index  index.html index.htm;
        }
        access_log  off;
    }

}
```
* __运行使能 KAE+ 参数调优过的 Nginx 同步模式的配置文件__    
```bash
/usr/local/nginx/sbin/nginx -s stop || true; sleep 1;
OPENSSL_CONF=/home/openssl.cnf /usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx_kae.conf
```
  
## 安装测压软件
### 1. 安装编译依赖
```bash
yum install -y gnutls-devel libev-devel
```
### 2. 下载源码包
```bash
git clone https://github.com/yarosla/httpress.git
```
### 3. 编译并安装
```bash
# 进入目录并编译
cd httpress && make
# 安装到系统路径
cp bin/Release/httpress /usr/bin
```
  
## 部署 copilot
* 详细安装方法参见[EulerCopilot Tune 安装使用指南](../../README.md)

### 1. 下载 copilot 源码
```bash
git clone https://gitee.com/openeuler/A-Tune.git
cd A-Tune/
# 切换到 euler-copilot-tune 分支
git checkout euler-copilot-tune
```
### 2. 安装系统依赖
```bash
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
### 3. 修改配置文件
*  __环境信息 config/.env.yaml 配置__
```YAML
# LLM 服务配置示例
# 根据实际使用的模型服务（如 OpenAI、通义千问、deepseek 等）填写以下字段
LLM_KEY: "sk-XXXXXX"                    # 必填：模型服务的 API 密钥
LLM_URL: "https://api.deepseek.com"     # 必填：LLM 服务的 API 接口地址，如 "https://api.deepseek.com"
LLM_MODEL_NAME: "deepseek-chat"         # 必填：要调用的模型名，如 deepseek-chat
LLM_MAX_TOKENS:                         # 选填：生成文本的最大 token 数，如512或2048

# 部署应用的机器 ip 信息（重点补充 ip、host_user、password）
servers:
  - ip: ""                              # 必填：服务器 IP 
    host_user: ""                       # 必填：主机用户名
    password: ""                        # 必填：登录密码
    port: 22                            # SSH端口，默认22
    app: "nginx"
    listening_address: "127.0.0.1"      # 必填：服务监听地址
    listening_port: "10000"             # 必填：服务监听端口
    target_process_name: "nginx"
    business_context: "高并发Web服务，CPU负载主要集中在用户态处理"
    max_retries: 3
    delay: 1.0
```
* __应用部署信息 config/app_config.yaml 配置__        
需按实际环境填写；一般无需修改，若部署方式不同需要修改对应命令。
```YAML
nginx:
  port: 10000
  config_file: "/usr/local/nginx/conf/nginx.conf"
  # 设置某个参数的模板
  set_param_template: 'grep -q "^\\s*$param_name\\s\\+" "$config_file" && sed -i "s|^\\s*$param_name\\s\\+.*|    $param_name $param_value;|" "$config_file" || sed -i "/http\\s*{/a\    $param_name $param_value;" "$config_file"'
  # 获取某个参数的模板
  get_param_template: 'grep -E "^\\s*$param_name\\s+" $config_file | head -1 | sed -E "s/^\\s*$param_name\\s+(.*);/\\1/"'
  stop_workload: "/usr/local/nginx/sbin/nginx -s reload"
  start_workload: "/usr/local/nginx/sbin/nginx -s reload"
  # 压测脚本
  benchmark: "$EXECUTE_MODE:local sh $SCRIPTS_DIR/nginx/parse_benchmark.sh $host_ip $port"
  performance_metric: "QPS"

```

* __scripts/nginx/benchmark.sh 脚本内容：__
```YAML
#!/bin/sh
echo 1 > /tmp/euler-copilot-fifo

retry_num=0
csv_file="rps_result_matuner.csv"

# 初始化 CSV 文件，添加表头（如果不存在）
if [ ! -f "$csv_file" ]; then
    echo "rps,kbps" > "$csv_file"
fi
while [ $retry_num -le 5 ]
do
    httpress -n 20000000 -c 512 -t 7 -k http://localhost:10000 > benchmark_result 2>&1
    if [ $? == 0 ];then
        cat benchmark_result
        rps=$(cat benchmark_result | grep 'TIMING:' | awk '{print $4}')
        kbps=$(cat benchmark_result | grep 'TIMING:' | awk '{print $6}')

        echo "${rps},${kbps}" >> "$csv_file"
        break
    fi
    retry_num=$((retry_num + 1))
done
```

### 4. 执行调优程序
```bash
# 在源码根目录执行
export PYTHONPATH="`pwd`:$PYTHONPATH"
python3 src/start_tune.py
```