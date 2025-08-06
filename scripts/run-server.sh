#!/bin/bash
# 获取当前脚本所在的目录（即 scripts/ 目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# 获取项目根目录（假设 run-server.sh 在 scripts/ 下，项目根目录是 scripts/ 的上级目录）
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 将项目根目录添加到 PYTHONPATH
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"
echo "🔧 PYTHONPATH set to: $PYTHONPATH"

# 引入参数配置
# 获取当前脚本所在目录（即 scripts/）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 从 scripts/ 目录加载 run-param.sh
if [[ -f "$SCRIPT_DIR/run-param.sh" ]]; then
    source "$SCRIPT_DIR/run-param.sh"
else
    echo "❌ Error: run-param.sh not found in $SCRIPT_DIR"
    exit 1
fi

echo " An AI Agent write Umamusume Novel - Server Start "
echo "Please ensure your Python virtual environment is activated:"
echo "  source .venv/bin/activate"
echo "  # or"
echo "  conda activate umamusume-novel"
echo "==================================================================================================================="

# 获取用户输入的端口（如果未提供则使用默认值）
RAG_PORT=${1:-$DEFAULT_RAG_PORT}
WEB_PORT=${2:-$DEFAULT_WEB_PORT}
SERVER_PORT=${3:-$DEFAULT_SERVER_PORT}

echo "🔧 Using ports:"
echo "   Rag MCP:        http://127.0.0.1:$RAG_PORT"
echo "   Web MCP:        http://127.0.0.1:$WEB_PORT"
echo "   Server & Client: http://127.0.0.1:$SERVER_PORT/ask"
echo ""

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_RAG")" "$(dirname "$LOG_WEB")" "$(dirname "$LOG_SERVER")"

# 清空或创建日志文件 (使用 > 并确保目录存在)
> "$LOG_RAG"
> "$LOG_WEB"
> "$LOG_SERVER"

# 清空或创建pid文件
> .rag.pid
> .web.pid
> .server.pid

# --- 启动 raginfomcp.py 使用 uvicorn ---
# 注意：模块路径使用点号(.)分隔，对应 src/umamusume_novel/rag/raginfomcp.py 中的 rag_mcp_app
nohup uvicorn umamusume_novel.rag.raginfomcp:rag_mcp_app \
  --host 127.0.0.1 --port "$RAG_PORT" \
  --log-level info > "$LOG_RAG" 2>&1 &
RAG_PID=$!
echo $RAG_PID > .rag.pid
echo "🚀 Started raginfomcp.py with uvicorn (PID: $RAG_PID)"

# --- 启动 webinfomcp.py 使用 uvicorn ---
# 注意：模块路径使用点号(.)分隔，对应 src/umamusume_novel.web.webinfomcp.py 中的 web_mcp_app
nohup uvicorn umamusume_novel.web.webinfomcp:web_mcp_app \
  --host 127.0.0.1 --port "$WEB_PORT" \
  --log-level info > "$LOG_WEB" 2>&1 &
WEB_PID=$!
echo $WEB_PID > .web.pid
echo "🚀 Started webinfomcp.py with uvicorn (PID: $WEB_PID)"

# --- 等待两个服务启动完成 ---
# 等待 uvicorn 启动成功的日志出现
echo "⏳ Waiting for Rag MCP (port $RAG_PORT) and Web MCP (port $WEB_PORT) servers to start..."
# 使用 timeout 避免无限等待
WAIT_TIMEOUT=60 # 秒
WAIT_COUNT=0
SLEEP_INTERVAL=2
until (grep -q "Uvicorn running on.*127.0.0.1:$RAG_PORT" "$LOG_RAG" && \
       grep -q "Uvicorn running on.*127.0.0.1:$WEB_PORT" "$LOG_WEB"); do
    if [ $WAIT_COUNT -ge $((WAIT_TIMEOUT / SLEEP_INTERVAL)) ]; then
        echo "❌ Timeout waiting for Rag or Web MCP to start. Check logs:"
        echo "   Rag Log: $LOG_RAG"
        echo "   Web Log: $LOG_WEB"
        # 尝试杀死已启动的进程
        kill $RAG_PID $WEB_PID 2>/dev/null
        exit 1
    fi
    echo "⏳ Still waiting... (Check logs if this takes too long)"
    sleep $SLEEP_INTERVAL
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

echo "✅ Rag MCP (port $RAG_PORT) and Web MCP (port $WEB_PORT) are ready."

# --- 启动主服务器 umamusume_create_novel.py (现在是 main.py) ---
# 注意：确保 main.py 的路径正确，并且它能接收 -w, -r, -p 参数
nohup python src/umamusume_novel/main.py \
    -p $SERVER_PORT \
    -w http://127.0.0.1:$WEB_PORT/mcp \
    -r http://127.0.0.1:$RAG_PORT/mcp > $LOG_SERVER 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > .server.pid
echo "🚀 Started main.py (umamusume_create_novel) (PID: $SERVER_PID)"

# --- 等待主服务器启动 (可以根据实际日志调整) ---
# 这里简单等待几秒，或者检查日志
sleep 5
# 或者更精确地等待特定日志 (示例，需要 main.py 实际输出匹配):
# until grep -q "服务器启动成功\|Server started" "$LOG_SERVER"; do
#     echo "⏳ Waiting for Main Server to start..."
#     sleep 2
# done
# echo "✅ Main Server is ready."

# --- 设置 trap 来确保退出时清理进程 ---
# kill 并等待进程结束
trap 'echo "🛑 Stopping servers..."; kill $RAG_PID $WEB_PID $SERVER_PID 2>/dev/null; wait $RAG_PID $WEB_PID $SERVER_PID 2>/dev/null; echo "🛑 All servers stopped."; exit' SIGINT SIGTERM EXIT

echo "🟢 All servers started successfully. Press Ctrl+C to stop."
# --- 等待中断信号 (Ctrl+C) ---
# trap 会在 wait 被中断后执行清理
wait $RAG_PID $WEB_PID $SERVER_PID # 等待所有后台进程

# 如果 wait 因为进程退出而返回（非信号中断）
echo "⚠️  One or more servers exited unexpectedly."
# trap 的 EXIT 处理仍会运行