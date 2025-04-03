# 本地文件检查与等待逻辑
LOG_FILE="PATH/tpcc/mariadb_tpmc.out"
MAX_WAIT=60
for ((i=0; i<MAX_WAIT; i++)); do
    # 如果文件存在，打印信息并继续
    if [ -f "$LOG_FILE" ]; then
        break
    fi
    # 如果文件不存在，等待1秒
    sleep 1
done

# 如果超时后文件仍然不存在，退出
if [ ! -f "$LOG_FILE" ]; then
    echo "Local file $LOG_FILE does not exist after waiting $MAX_WAIT seconds!"
    exit 1
fi

# 获取本地文件内容
local_value=$(cat PATH/mariadb_tpmc.out)

# 检查远程文件是否存在并获取内容
ssh -q root@CLIENT_IP_2 'sleep 1'
remote_value=$(ssh -q root@CLIENT_IP_2 'if [ -f PATH/tpcc/mariadb_tpmc.out ]; then cat PATH/tpcc/mariadb_tpmc.out; else echo "Remote file does not exist!"; exit 1; fi')

# 将两个值相加并输出结果
sum=$((local_value + remote_value))
echo $sum
