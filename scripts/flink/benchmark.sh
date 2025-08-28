#!/bin/bash

echo 1 > /tmp/euler-copilot-fifo
docker exec -i flink_jm_8c32g bash -c "source /etc/profile && /usr/local/flink-1.16.3/bin/stop-cluster.sh && /usr/local/nexmark/bin/shutdown_cluster.sh && /usr/local/flink-1.16.3/bin/start-cluster.sh && /usr/local/nexmark/bin/setup_cluster.sh && cd /usr/local/nexmark/bin && ./run_query.sh q0"  > /home/wsy/benchmark.log 2>&1
