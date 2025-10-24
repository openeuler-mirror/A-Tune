#!/bin/bash
# 功能：根据参数 scope 自动选择 observer / obproxy 设置参数
# 用法：
#  初始设置时
#   ./set_param.sh <param_name> <value> <observer_ip> <observer_password> <proxy_ip> <proxy_password> <copilot_path>
#  参数设置时：
#   ./set_param.sh <param_name> <value>

PARAM=$1
VALUE=$2
OBSERVERIP=$3
OBSERVERPD=$4
PROXYIP=$5
PROXYPD=$6
COPILOTPATH=$7

# ===== 用户配置区 =====
OBCLIENT_OBSERVER="obclient -h$OBSERVERIP -P2881 -uroot@sys -p$OBSERVERPD -Doceanbase -A"
OBCLIENT_PROXY="obclient -h$PROXYIP -P2883 -uroot@proxysys -p$PROXYPD -Doceanbase -A"
PARAM_FILE="$COPILOTPATH/A-Tune-euler-copilot-tune/src/knowledge_base/knob_params/oceanbase.json"
# =======================

if [ $# -lt 2 ]; then
    echo "用法：$0 <param_name> <value>"
    exit 1
fi

# 校验参数文件
if [ ! -f "$PARAM_FILE" ]; then
    echo "错误：找不到参数文件 $PARAM_FILE"
    exit 1
fi

# 从 JSON 提取 scope
SCOPE=$(jq -r --arg name "$PARAM" '.[$name].scope' "$PARAM_FILE")

if [ "$SCOPE" == "null" ] || [ -z "$SCOPE" ]; then
    echo "❌  未在参数文件中找到 $PARAM"
    exit 1
fi

# ---------- 设置 ----------
case "$SCOPE" in
  observer)
    REMOTE_CMD="$OBCLIENT_OBSERVER -e \"ALTER SYSTEM SET $PARAM = $VALUE;\""
    ssh -q root@$OBSERVERIP "$REMOTE_CMD"
    ;;
  obproxy)
    REMOTE_CMD="$OBCLIENT_PROXY -e \"ALTER PROXYCONFIG SET $PARAM = $VALUE;\""
    ssh -q root@$OBSERVERIP "$REMOTE_CMD"
    ;;
  *)
    echo "❌  未知scope类型：$SCOPE"
    ;;
esac