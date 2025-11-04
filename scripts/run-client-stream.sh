#!/bin/bash

# 赛马娘同人文客户端 - 流式模式启动脚本

echo "=============================================="
echo "  赛马娘同人文客户端 - 流式模式"
echo "=============================================="
echo ""

# 检查服务器地址参数
SERVER_URL=${1:-"http://127.0.0.1:1111"}

echo "服务器地址: $SERVER_URL"
echo "模式: 流式"
echo ""
echo "使用方法:"
echo "  ./scripts/run-client-stream.sh [服务器地址]"
echo ""
echo "示例:"
echo "  ./scripts/run-client-stream.sh"
echo "  ./scripts/run-client-stream.sh http://127.0.0.1:1111"
echo ""
echo "=============================================="
echo ""

# 启动客户端
python -m src.umamusume_novel.client.cli -u "$SERVER_URL" --stream

