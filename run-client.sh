#!/bin/bash

# 引入参数配置
source ./run-param.sh

# 允许用户传入自定义服务器端口
SERVER_PORT=${1:-$DEFAULT_SERVER_PORT}

echo " An AI Agent write Umamusume Novel - Client Start "
echo "run source .venv/bin/activate firstly"
echo "or run conda activate umamusume-novel"
echo "==================================================================================================================="

echo "💬 Starting client. You can now input questions."
python umamusume_client.py -u http://127.0.0.1:$SERVER_PORT/ask

echo "👋 Client exited."