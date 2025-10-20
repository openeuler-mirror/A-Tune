echo 1 > /tmp/euler-copilot-fifo
obd test sysbench obcluster --tenant=sysbench_tenant --script-name=oltp_read_only.lua --tables=30 --table-size=10000 --threads=32