# Kafka Tuning and Deployment

## Prerequisites

- To simulate a production environment, we need at least two hosts, a server and a client.

- The /tmp/ on the server must be more significant than 2GB because the server will receive the massive amount of data sent by the client and write it to /tmp/.You can follow the steps below to increase the size.

  ```bash
  mount -o remount,size=10G /tmp/
  ```

## Deployment ⚙️

Before tuning, we need to deploy Kafka first.

You can download the Kafka release tarball(<https://dlcdn.apache.org/kafka/3.2.0/kafka_2.13-3.2.0.tgz>) and put it under this directory so that the deployment script will skip the download. This tarball will be sent to the client by scp cause we will use the benchmark tool included in it.

Running `prepare.sh` to deploy, follow the hint. The script will create a new ssh-key from server to client if not set up yet.

## About Scrpits

- `prepare.sh`, deploy the whole environment for tuning.
- `launcher_on_server.sh`, launch the `benchmark_on_client.sh` on the client, and copy the result log back to the server.
- `benchmark_on_client.sh`, do Kafka producer and consumer test, generate result log.
- `manager.sh`, control the Kafka service.

## Tuning 🔧

After running the deployment script, copy the server-side YAML which you want to use to **/etc/atuned/tuning/**

### Start to tuning

atune-adm tuning --project PROJECT --detail ./CLIENT.yaml

eg: atune-adm tuning --project kafka --detail ./kafka.yaml

### Restore the environment

atune-adm tuning --restore --project PROJECT
eg: atune-adm tuning --restore --project kafka

## To contact ✉️

- Email: me@shangcode.cn
- Gitee: https://gitee.com/shangyingjie
