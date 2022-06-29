# Deployment script for Redis and its benchmark

Before running the script, you may want to read this guide first.

The goal is to deploy redis-server on localhost, redis-benchmark on another host for future tunning work.

## Deploy ⚙️

To run the script, execute `bash prepare.sh`.

1. Enter the IP address and port number(skip to default) of the redis-server host.
2. Enter the IP address of the redis-benchmark host.
3. Enter 'y' to generate and deploy the new SSH key on the benchmark host, or skip if the SSH key is configured.
4. Enter the password for access benchmark host.

That is all you need to interact with the script.

## Benchmark ⏱️

To start the benchmark, execute `bash redis_benchmark.sh`, the localhost will access the benchmark host and trigger it.

The benchmark host will transfer the log file to localhost after the benchmark.

## Tunning 🔧
There are currently two server-side YAML files, and you can choose to use one of them.

After running the deployment script, copy the server-side YAML which you want to use to **/etc/atuned/tuning/**

### Modify Server-side YAML (optional)
Some parameters are unsuitable for all scenarios, so I write a particular bash script and corresponding options.

If some are not suitable for your scenarios, remove the option which could trigger the script to modify the system.

Including: `redis.RDB`, `redis.AOF` and `redis.unixsocket`.

Use `redis.unixsocket` as an example.
According to Redis official documentaion:
https://redis.io/docs/reference/optimization/benchmarks/#factors-impacting-redis-performance
> When the server and client benchmark programs run on the same box, both the TCP/IP loopback and unix domain sockets can be used. Depending on the platform, unix domain sockets can achieve around 50% more throughput than the TCP/IP loopback (on Linux for instance). The default behavior of redis-benchmark is to use the TCP/IP loopback.

So, if you want to enable this parameter, add a "yes" option to it.

```yaml
  - name: "redis.unixsocket"
    info:
      desc: "use unix domain sockets to communicate.(benefit when client and server running on same box)"
      get: value="not set"; if grep -P '^maxclients' /etc/redis.conf; then value="$(grep -P '^unixsocket' /etc/redis.conf)"; fi ;echo "${value}"
      set: if [ "$value" = "yes" ]; then sed -i "/# unixsocketperm /a unixsocket /tmp/redis.sock" ./test; sed -i "/^unixsocket /a unixsocketperm 700" ./test; fi
      needrestart: "true"
      type: "discrete"
      dtype: "string"
      options:
        - "no"
        - "yes"

```

### Start to tuning
atune-adm tuning --project PROJECT --detail ./CLIENT.yaml

eg: atune-adm tuning --project redis --detail ./redis_client.yaml

### Restore the environment
atune-adm tuning --restore --project PROJECT

eg: atune-adm tuning --restore --project redis


## To contact ✉️
### chengyu
- Gitee: https://gitee.com/mccyb
### yingjie
- Email: yingjie@isrc.iscas.ac.cn
- Gitee: https://gitee.com/shangyingjie
