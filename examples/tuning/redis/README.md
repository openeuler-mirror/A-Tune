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

To start the benchmark, execute `bash benchmark.sh`, the localhost will access the benchmark host and trigger it.

The benchmark host will transfer the log file to localhost after the benchmark.

## To contact ✉️

- Email: yingjie@isrc.iscas.ac.cn
- Gitee: https://gitee.com/shangyingjie
