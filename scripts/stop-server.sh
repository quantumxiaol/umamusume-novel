#!/bin/bash

# 如果使用 
# nohup ./run-server.sh > server_output.log 2>&1 &
# 来挂载服务，需要使用 bash stop-server.sh来终止脚本
# 获取当前脚本所在目录（scripts/）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 获取项目根目录（scripts/ 的上一级目录）
PROJECT_ROOT="$(cd "$SCRIPT_DIR"/.. && pwd)"

echo "正在从目录: $PROJECT_ROOT 停止服务..."

# 定义 PID 文件路径
RAG_PID_FILE="$PROJECT_ROOT/.rag.pid"
WEB_PID_FILE="$PROJECT_ROOT/.web.pid"
SERVER_PID_FILE="$PROJECT_ROOT/.server.pid"

# --- 停止 Rag MCP 服务 ---
if [[ -f "$RAG_PID_FILE" ]]; then
    RAG_PID=$(cat "$RAG_PID_FILE")
    if kill "$RAG_PID" 2>/dev/null; then
        rm -f "$RAG_PID_FILE"
        echo "✅ Rag MCP 服务 (PID: $RAG_PID) 已停止"
    else
        echo "❌ 无法停止 Rag MCP (PID: $RAG_PID)，可能已退出或无权限"
        rm -f "$RAG_PID_FILE"  # 清理残留 PID 文件
    fi
else
    echo "Rag MCP 未运行（PID 文件不存在）"
fi

# --- 停止 Web MCP 服务 ---
if [[ -f "$WEB_PID_FILE" ]]; then
    WEB_PID=$(cat "$WEB_PID_FILE")
    if kill "$WEB_PID" 2>/dev/null; then
        rm -f "$WEB_PID_FILE"
        echo "✅ Web MCP 服务 (PID: $WEB_PID) 已停止"
    else
        echo "❌ 无法停止 Web MCP (PID: $WEB_PID)，可能已退出或无权限"
        rm -f "$WEB_PID_FILE"
    fi
else
    echo "Web MCP 未运行（PID 文件不存在）"
fi

# --- 停止主服务（小说生成服务） ---
if [[ -f "$SERVER_PID_FILE" ]]; then
    SERVER_PID=$(cat "$SERVER_PID_FILE")
    if kill "$SERVER_PID" 2>/dev/null; then
        rm -f "$SERVER_PID_FILE"
        echo "✅ 主服务 (PID: $SERVER_PID) 已停止"
    else
        echo "❌ 无法停止主服务 (PID: $SERVER_PID)，可能已退出或无权限"
        rm -f "$SERVER_PID_FILE"
    fi
else
    echo "  主服务未运行（PID 文件不存在）"
fi

echo "所有服务停止完成。"