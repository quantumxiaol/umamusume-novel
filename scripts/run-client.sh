#!/bin/bash
# 获取当前脚本所在目录（即 scripts/）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 引入参数配置
# 从 scripts/ 目录加载 run-param.sh
if [[ -f "$SCRIPT_DIR/run-param.sh" ]]; then
    source "$SCRIPT_DIR/run-param.sh"
else
    echo "❌ Error: run-param.sh not found in $SCRIPT_DIR"
    exit 1
fi

# 允许用户传入自定义服务器端口
SERVER_PORT=${1:-$DEFAULT_SERVER_PORT}

echo " An AI Agent write Umamusume Novel - Client Start "
echo "run source .venv/bin/activate firstly"
echo "or run conda activate umamusume-novel"
echo "==================================================================================================================="

echo "💬 Starting client. You can now input questions."
python umamusume_client.py -u http://127.0.0.1:$SERVER_PORT/ask

echo "👋 Client exited."