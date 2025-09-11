# 获取目标地址和端口
TARGET_HOST="$1"
TARGET_PORT="$2"
echo 1 > /tmp/euler-copilot-fifo
httpress -n 20000000 -c 512 -t 7 -k http://${TARGET_HOST}:${TARGET_PORT}