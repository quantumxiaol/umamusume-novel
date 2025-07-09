#!/bin/bash

echo " An AI Agent wirght Umamusume Novel "
echo "run source .venv/bin/activate firstly"
echo "or run conda activate umamusume-novel"
echo "==================================================================================================================="

# 默认端口号设置
DEFAULT_RAG_PORT=7778
DEFAULT_WEB_PORT=7777
DEFAULT_SERVER_PORT=1111  # 客户端和服务器共用这个端口通信

# 日志文件名（带 .log 后缀）
LOG_RAG="lograg.log"
LOG_WEB="logweb.log"
LOG_SERVER="logserver.log"

# 获取用户输入的端口（如果未提供则使用默认值）
RAG_PORT=${1:-$DEFAULT_RAG_PORT}
WEB_PORT=${2:-$DEFAULT_WEB_PORT}
SERVER_PORT=${3:-$DEFAULT_SERVER_PORT}

echo "🔧 Using ports:"
echo "   Rag MCP:        127.0.0.1:$RAG_PORT"
echo "   Web MCP:        127.0.0.1:$WEB_PORT"
echo "   Server & Client: http://127.0.0.1:$SERVER_PORT/ask"
echo ""

# 清空或创建日志文件
> $LOG_RAG
> $LOG_WEB
> $LOG_SERVER

# 启动 raginfomcp.py
nohup python raginfomcp.py -p $RAG_PORT > $LOG_RAG 2>&1 &
RAG_PID=$!
echo "🚀 Started raginfomcp.py (PID: $RAG_PID)"

# 启动 webinfomcp.py
nohup python webinfomcp.py -p $WEB_PORT > $LOG_WEB 2>&1 &
WEB_PID=$!
echo "🚀 Started webinfomcp.py (PID: $WEB_PID)"

# 等待两个服务启动完成
until grep -q "Uvicorn running on" "$LOG_RAG" && grep -q "Uvicorn running on" "$LOG_WEB"; do
    echo "⏳ Waiting for Rag MCP and Web MCP servers to start..."
    sleep 2
done

echo "✅ Rag MCP and Web MCP are ready."

# 启动 umamusume_create_novel.py（Server）
nohup python umamusume_create_novel.py -p $SERVER_PORT \
    -w http://127.0.0.1:$WEB_PORT/mcp \
    -r http://127.0.0.1:$RAG_PORT/mcp > $LOG_SERVER 2>&1 &
SERVER_PID=$!
echo "🚀 Started umamusume_create_novel.py (PID: $SERVER_PID)"

# 等待 server 启动
sleep 5

# 运行客户端测试脚本，允许用户输入问题
echo "💬 Starting client. You can now input questions."
python umamusume_client.py -u http://127.0.0.1:$SERVER_PORT/ask

# 客户端退出后，杀死前面的后台进程
echo "🛑 Killing background processes..."
kill $RAG_PID $WEB_PID $SERVER_PID 2>/dev/null

# 显示日志尾部便于调试
echo "📄 Last logs:"
tail -n 10 $LOG_RAG $LOG_WEB $LOG_SERVER