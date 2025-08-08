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
SERVER_URL="http://127.0.0.1:$SERVER_PORT/ask"

# 可选问题（用于非交互模式）
shift $((1))
QUESTION="$*"

echo " An AI Agent write Umamusume Novel - Client Start "
echo "run source .venv/bin/activate firstly"
echo "or run conda activate umamusume-novel"
echo "==================================================================================================================="

echo "💬 Starting client. You can now input questions."

CMD=("python" "-m" "umamusume_novel.client.cli" "-u" "$SERVER_URL")

if [[ -n "$QUESTION" ]]; then
    CMD+=("-q" "$QUESTION")
fi

# 执行
echo "💬 Starting client..."
"${CMD[@]}"


echo "👋 Client exited."