import uvicorn
import argparse
import asyncio
import subprocess
import sys
import os
import signal
import time
from pathlib import Path

# --- 配置和常量 ---
# 在这里定义默认值

DEFAULT_RAG_PORT = 7777
DEFAULT_WEB_PORT = 7778
DEFAULT_SERVER_PORT = 1111
DEFAULT_HOST = "127.0.0.1"

LOGS_DIR = "./logs"
os.makedirs(LOGS_DIR, exist_ok=True) # 确保日志目录存在

# --- 全局变量用于管理子进程 ---
_processes_to_cleanup = []
def howtorun():
    print("Hello from umamusume-novel!")
    print("bash ./scripts/run-server.sh")
    print("bash ./scripts/run-client.sh")
# --- 工具函数 ---
def cleanup():
    """清理所有启动的子进程"""
    global _processes_to_cleanup
    print("\n🛑 Shutting down all services...")
    for process in _processes_to_cleanup:
        if process and process.poll() is None: # 如果进程还在运行
            try:
                # 尝试优雅关闭
                process.terminate()
                process.wait(timeout=5)
                print(f"   -> Process {process.args[0]} (PID: {process.pid}) terminated gracefully.")
            except subprocess.TimeoutExpired:
                print(f"   -> Process {process.args[0]} (PID: {process.pid}) timed out, forcing kill.")
                process.kill()
                process.wait()
            except Exception as e:
                print(f"   -> Error stopping process {process.args[0]} (PID: {process.pid}): {e}")
        else:
            print(f"   -> Process {process.args[0] if process else 'N/A'} (PID: {process.pid if process else 'N/A'}) already exited.")
    _processes_to_cleanup = []
    print("✅ All services stopped.")

def signal_handler(signum, frame):
    """处理 SIGINT (Ctrl+C)"""
    print(f"\n🛑 Received signal {signum}.")
    cleanup()
    sys.exit(0)

async def wait_for_logs(log_file_path: str, success_indicators: list, timeout: int = 60) -> bool:
    """等待日志文件中出现任一成功的标志"""
    log_file_path = Path(log_file_path)
    print(f"⏳ Waiting for log indicator in {log_file_path.name} (Timeout: {timeout}s)")
    print(f"   Looking for: {success_indicators}")
    wait_count = 0
    sleep_interval = 2
    while wait_count < timeout / sleep_interval:
        if log_file_path.exists():
            try:
                with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for indicator in success_indicators:
                        if indicator in content:
                            print(f"✅ Found indicator '{indicator}' in {log_file_path.name}.")
                            return True
            except Exception as e:
                print(f"⚠️  Error reading log {log_file_path.name}: {e}")
        await asyncio.sleep(sleep_interval)
        wait_count += 1
    print(f"❌ Timeout waiting for indicator in {log_file_path.name}.")
    return False

# --- 服务启动函数 ---
async def start_rag_mcp(rag_port: int):
    """启动 RAG MCP 服务"""
    global _processes_to_cleanup
    cmd = [
        sys.executable, "-m", "uvicorn",
        "umamusume_novel.rag.raginfomcp:rag_mcp_app",
        "--host", DEFAULT_HOST, "--port", str(rag_port),
        "--log-level", "info"
    ]
    log_file = f"{LOGS_DIR}/rag_mcp.log"
    print(f"🚀 Starting RAG MCP: {' '.join(cmd)}")
    with open(log_file, 'w') as f_log:
        process = subprocess.Popen(cmd, stdout=f_log, stderr=subprocess.STDOUT)
    _processes_to_cleanup.append(process)
    print(f"   -> RAG MCP PID: {process.pid}, Log: {log_file}")
    return process, log_file

async def start_web_mcp(web_port: int):
    """启动 Web MCP 服务"""
    global _processes_to_cleanup
    cmd = [
        sys.executable, "-m", "uvicorn",
        "umamusume_novel.web.webinfomcp:web_mcp_app",
        "--host", DEFAULT_HOST, "--port", str(web_port),
        "--log-level", "info"
    ]
    log_file = f"{LOGS_DIR}/web_mcp.log"
    print(f"🚀 Starting Web MCP: {' '.join(cmd)}")
    with open(log_file, 'w') as f_log:
        process = subprocess.Popen(cmd, stdout=f_log, stderr=subprocess.STDOUT)
    _processes_to_cleanup.append(process)
    print(f"   -> Web MCP PID: {process.pid}, Log: {log_file}")
    return process, log_file

async def start_main_server(server_port: int, rag_port: int, web_port: int):
    """启动主小说生成服务器"""
    global _processes_to_cleanup
    cmd = [
        sys.executable, "src/umamusume_novel/main.py", # 注意：这是 src/umamusume_novel/main.py
        "-p", str(server_port),
        "-w", f"http://{DEFAULT_HOST}:{web_port}/mcp",
        "-r", f"http://{DEFAULT_HOST}:{rag_port}/mcp",
    ]
    log_file = f"{LOGS_DIR}/server.log"
    print(f"🚀 Starting Main Server: {' '.join(cmd)}")
    with open(log_file, 'w') as f_log:
        # 使用 subprocess.Popen 而非 asyncio.create_subprocess_exec
        # 因为我们希望它在前台运行并阻塞，直到用户想退出
        process = subprocess.Popen(cmd, stdout=f_log, stderr=subprocess.STDOUT)
    _processes_to_cleanup.append(process)
    print(f"   -> Main Server PID: {process.pid}, Log: {log_file}")
    return process, log_file

async def run_client(server_port: int):
    """启动客户端"""
    cmd = [
        sys.executable, "umamusume_client.py", # 假设在项目根目录
        "-u", f"http://{DEFAULT_HOST}:{server_port}/ask"
    ]
    print(f"💬 Starting Client: {' '.join(cmd)}")
    # 客户端是交互式的，让它在前台运行并接管终端
    # 使用 subprocess.run 会阻塞，直到客户端退出
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Client exited with error: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Client interrupted by user.")

# --- 主逻辑 ---
async def run_full_stack(rag_port: int, web_port: int, server_port: int, start_client: bool):
    """运行完整的应用栈"""
    global _processes_to_cleanup

    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGTERM, signal_handler) # 主进程用 Ctrl+C 即可

    print("==========================================")
    print(" An AI Agent write Umamusume Novel - Full Stack Start ")
    print(" Please ensure your Python virtual environment is activated.")
    print("==========================================")
    print(f"🔧 Ports: RAG={rag_port}, Web={web_port}, Server={server_port}")
    print("")

    try:
        # 1. 启动 RAG 和 Web MCP (并发)
        print("🚀 Initiating MCP services startup...")
        rag_task = start_rag_mcp(rag_port)
        web_task = start_web_mcp(web_port)
        
        rag_process, rag_log = await rag_task
        web_process, web_log = await web_task

        # 2. 等待 RAG 和 Web MCP 就绪 (并发等待)
        rag_indicator = [f"Uvicorn running on http://{DEFAULT_HOST}:{rag_port}"]
        web_indicator = [f"Uvicorn running on http://{DEFAULT_HOST}:{web_port}"]
        
        wait_rag_task = wait_for_logs(rag_log, rag_indicator, timeout=60)
        wait_web_task = wait_for_logs(web_log, web_indicator, timeout=60)

        rag_ready, web_ready = await asyncio.gather(wait_rag_task, wait_web_task)

        if not (rag_ready and web_ready):
            print("❌ Failed to start one or more MCP services. Exiting.")
            cleanup()
            sys.exit(1)

        print("✅ All MCP services are ready.")

        # 3. 启动主服务器
        print("🚀 Initiating Main Server startup...")
        server_process, server_log = await start_main_server(server_port, rag_port, web_port)
        
        # 4. 等待主服务器就绪 (简单等待或检查日志)
        server_indicator = [f"Uvicorn running on http://{DEFAULT_HOST}:{server_port}", "Application startup complete"]
        server_ready = await wait_for_logs(server_log, server_indicator, timeout=30)
        
        if not server_ready:
            print("❌ Main Server failed to start in time. Exiting.")
            cleanup()
            sys.exit(1)
        
        print("✅ Main Server is ready.")

        # 5. 启动客户端 (如果需要)
        if start_client:
            print("🚀 Initiating Client startup...")
            await run_client(server_port)
        else:
            print("🟢 All services are running in the background.")
            print(f"   🌐 Main Server: http://{DEFAULT_HOST}:{server_port}/ask")
            print(f"   📄 Logs are in the '{LOGS_DIR}' directory.")
            print("   🛑 Press Ctrl+C in this terminal to stop all services.")
            # 如果不启动客户端，主进程需要等待中断信号
            try:
                # 简单地等待，直到收到 SIGINT
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                pass # 允许信号处理函数接管

    except Exception as e:
        print(f"\n💥 Unexpected error during startup: {e}")
    finally:
        cleanup()
        print("👋 Full stack shutdown complete.")

# --- 命令行入口 ---
def main():
    parser = argparse.ArgumentParser(
        description="启动赛马娘小说生成完整服务栈 (RAG MCP, Web MCP, Main Server) 并可选启动客户端",
        formatter_class=argparse.RawTextHelpFormatter # 保持帮助文本格式
    )
    parser.add_argument(
        "action",
        nargs='?', 
        choices=['server-only', 'with-client'],
        default='server-only',
        help=(
            "启动模式:\n"
            "  server-only   - 仅启动服务 (RAG, Web, Main Server) 并在后台运行 (默认)\n"
            "  with-client   - 启动服务并立即启动客户端进行交互"
        )
    )
    parser.add_argument("-rp", "--rag-port", type=int, default=DEFAULT_RAG_PORT, help=f"RAG MCP 端口 (默认: {DEFAULT_RAG_PORT})")
    parser.add_argument("-wp", "--web-port", type=int, default=DEFAULT_WEB_PORT, help=f"Web MCP 端口 (默认: {DEFAULT_WEB_PORT})")
    parser.add_argument("-sp", "--server-port", type=int, default=DEFAULT_SERVER_PORT, help=f"主服务器端口 (默认: {DEFAULT_SERVER_PORT})")
    
    args = parser.parse_args()

    start_client = (args.action == 'with-client')

    # 运行异步主函数
    try:
        asyncio.run(run_full_stack(args.rag_port, args.web_port, args.server_port, start_client))
    except KeyboardInterrupt:
        print("\n🛑 KeyboardInterrupt received in main.")
    except Exception as e:
        print(f"\n💥 Unexpected error in main process: {e}")
    finally:
        cleanup()





if __name__ == "__main__":
    main()
