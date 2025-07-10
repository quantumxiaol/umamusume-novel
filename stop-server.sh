#!/bin/bash

# 如果使用 
# nohup ./run.sh > server_output.log 2>&1 &
# 来挂载服务，需要使用 bash stop-server.sh来终止脚本

# 停止 Rag MCP 服务
if [ -f ".rag.pid" ]; then
    # 从 .rag.pid 文件中读取进程 ID 并终止
    kill $(cat .rag.pid) 2>/dev/null && rm -f .rag.pid
    echo "✅ 已停止 Rag MCP 服务"
else
    echo "❌ Rag MCP 未运行 或 PID 文件不存在"
fi

# 停止 Web MCP 服务
if [ -f ".web.pid" ]; then
    kill $(cat .web.pid) 2>/dev/null && rm -f .web.pid
    echo "✅ 已停止 Web MCP 服务"
else
    echo "❌ Web MCP 未运行 或 PID 文件不存在"
fi

# 停止主服务（小说生成服务）
if [ -f ".server.pid" ]; then
    kill $(cat .server.pid) 2>/dev/null && rm -f .server.pid
    echo "✅ 已停止主服务（小说创作）"
else
    echo "❌ 主服务未运行 或 PID 文件不存在"
fi