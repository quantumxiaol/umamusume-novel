#!/bin/bash

# 部署脚本：启动后端服务和前端开发服务器
# 用法: bash scripts/deploy.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

BACKEND_PID_FILE="$PROJECT_ROOT/.deploy_backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.deploy_frontend.pid"

# 清理函数
cleanup() {
    echo ""
    echo "🛑 正在停止所有服务..."
    [ -f "$FRONTEND_PID_FILE" ] && kill $(cat "$FRONTEND_PID_FILE") 2>/dev/null
    [ -f "$BACKEND_PID_FILE" ] && kill -SIGINT $(cat "$BACKEND_PID_FILE") 2>/dev/null
    rm -f "$FRONTEND_PID_FILE" "$BACKEND_PID_FILE"
    echo "✅ 所有服务已停止"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo "=========================================="
echo "  赛马娘同人文生成系统 - 部署脚本"
echo "=========================================="
echo ""

cd "$PROJECT_ROOT" || exit 1
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

# 启动后端
echo "📡 [1/2] 启动后端服务..."
python main.py server-only &
echo $! > "$BACKEND_PID_FILE"
echo "   后端启动中，请查看 logs/ 目录下的日志"
echo ""

# 等待后端启动（main.py 内部有完善的健康检查）
echo "⏳ 等待后端就绪（约60秒）..."
sleep 60

# 启动前端
echo "🎨 [2/2] 启动前端服务..."
cd "$FRONTEND_DIR" || exit 1

# 如果没有依赖，先安装
[ ! -d "node_modules" ] && pnpm install

pnpm run dev &
echo $! > "$FRONTEND_PID_FILE"

echo ""
echo "=========================================="
echo "🎉 部署完成！"
echo "=========================================="
echo "📍 前端: http://localhost:5173"
echo "📍 后端: http://127.0.0.1:1111"
echo "📄 日志: logs/"
echo "🛑 按 Ctrl+C 停止所有服务"
echo "=========================================="

wait
