#!/bin/bash
# 功能：根据参数 scope 自动选择 observer / obproxy 查询参数
# 用法：
#  初始设置时
#   ./get_param.sh <param_name> <observer_ip> <observer_password> <proxy_ip> <proxy_password> <copilot_path>
#  参数获取时：
#   ./get_param.sh <param_name>

PARAM=$1
OBSERVERIP=$2
OBSERVERPD=$3
PROXYIP=$4
PROXYPD=$5
COPILOTPATH=$6

# ===== 用户配置区 =====
OBCLIENT_OBSERVER="obclient -h$OBSERVERIP -P2881 -uroot@sys -p$OBSERVERPD -Doceanbase -A"
OBCLIENT_PROXY="obclient -h$PROXYIP -P2883 -uroot@proxysys -p$PROXYPD -Doceanbase -A"
PARAM_FILE="$COPILOTPATH/A-Tune-euler-copilot-tune/src/knowledge_base/knob_params/oceanbase.json"
# =======================

if [ $# -lt 1 ]; then
    echo "用法：$0 <param_name>"
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

# ---------- 查询 ----------
case "$SCOPE" in
  observer)
    REMOTE_CMD="$OBCLIENT_OBSERVER -e \"SHOW PARAMETERS LIKE '$PARAM';\" | awk 'NR>3 && \$1==\"zone2\"{print \$7}'"
    ssh -q root@$OBSERVERIP "$REMOTE_CMD"
    ;;
  obproxy)
    REMOTE_CMD="$OBCLIENT_PROXY -e \"SHOW PROXYCONFIG LIKE '$PARAM';\" | awk -v name=\"$PARAM\" '\$1==name{print \$2}'"
    ssh -q root@$OBSERVERIP "$REMOTE_CMD"
    ;;
  *)
    echo "❌  未知scope类型：$SCOPE"
    ;;
esac