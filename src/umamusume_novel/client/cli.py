"""
赛马娘同人文生成客户端

使用方法:
    # 非流式模式（默认）
    python -m src.umamusume_novel.client.cli -u http://127.0.0.1:1145
    python -m src.umamusume_novel.client.cli -u http://127.0.0.1:1145 -q "写一篇爱慕织姬的甜甜同人文"
    
    # 流式模式
    python -m src.umamusume_novel.client.cli -u http://127.0.0.1:1145 --stream
    python -m src.umamusume_novel.client.cli -u http://127.0.0.1:1145 --stream -q "写一篇米浴的温馨故事"
"""

import argparse
import sys
from datetime import datetime
from .umamusume_client import UmamusumeClient


class Colors:
    """终端颜色"""
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    RED = '\033[0;31m'
    MAGENTA = '\033[0;35m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


class StreamHandler:
    """处理流式输出"""
    
    def __init__(self):
        self.novel_content = ''
        self.rag_result = ''
        self.web_result = ''
        self.current_status = ''
        self.error = None
        self.token_count = 0
        self.start_time = datetime.now()
        
    def handle_event(self, event: str, data: str):
        """处理流式事件"""
        if event == 'status':
            # 显示当前状态
            self.current_status = data
            print(f"\r{Colors.CYAN}[状态] {data}{Colors.NC}", end='', flush=True)
        
        elif event == 'rag_result':
            # RAG 搜索结果
            self.rag_result = data
            print(f"\r{Colors.GREEN}[RAG完成] 结果长度: {len(data)} 字符{Colors.NC}")
            # 显示前500字符
            if data:
                preview = data[:500] + ('...' if len(data) > 500 else '')
                print(f"{Colors.YELLOW}RAG结果预览:{Colors.NC}\n{preview}\n")
        
        elif event == 'web_result':
            # Web 搜索结果
            self.web_result = data
            print(f"\r{Colors.GREEN}[Web完成] 结果长度: {len(data)} 字符{Colors.NC}")
            # 显示前500字符
            if data:
                preview = data[:500] + ('...' if len(data) > 500 else '')
                print(f"{Colors.YELLOW}Web结果预览:{Colors.NC}\n{preview}\n")
        
        elif event == 'token':
            # 小说内容流式输出
            if self.token_count == 0:
                # 清除状态提示，开始显示小说
                print(f"\r{' ' * 100}\r", end='')
                print(f"\n{Colors.BOLD}📖 生成的小说:{Colors.NC}\n")
                print("-" * 60)
            
            self.novel_content += data
            self.token_count += 1
            # 实时显示内容
            print(data, end='', flush=True)
        
        elif event == 'done':
            # 完成
            if self.token_count > 0:
                print()
                print("-" * 60)
            elapsed = (datetime.now() - self.start_time).total_seconds()
            print(f"\n{Colors.GREEN}✓ 生成完成！{Colors.NC}")
            print(f"{Colors.BOLD}统计信息:{Colors.NC}")
            print(f"  • 耗时: {elapsed:.2f} 秒")
            print(f"  • Token块数: {self.token_count}")
            print(f"  • 总字符数: {len(self.novel_content)}")
            if elapsed > 0:
                print(f"  • 平均速度: {len(self.novel_content)/elapsed:.1f} 字符/秒")
        
        elif event == 'error':
            # 错误
            self.error = data
            print(f"\r{Colors.RED}[错误] {data}{Colors.NC}")
        
        else:
            # 未知事件
            print(f"\r{Colors.YELLOW}[未知事件] {event}: {data[:100]}{Colors.NC}")


def handle_question_stream(client: UmamusumeClient, question: str):
    """处理流式问答"""
    print(f"\n{Colors.BOLD}问题:{Colors.NC} {question}\n")
    print("=" * 60)
    
    handler = StreamHandler()
    
    try:
        client.chat_stream(question, handler.handle_event)
        print()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ 用户取消生成{Colors.NC}")
    except Exception as e:
        print(f"\n\n{Colors.RED}错误: {e}{Colors.NC}")


def handle_question_normal(client: UmamusumeClient, question: str):
    """处理非流式问答"""
    print(f"\n{Colors.BOLD}问题:{Colors.NC} {question}\n")
    print("=" * 60)
    print(f"{Colors.CYAN}正在生成中，请稍候...{Colors.NC}\n")
    
    try:
        result = client.chat(question)
        
        if 'error' in result:
            print(f"{Colors.RED}错误: {result['error']}{Colors.NC}")
            return
        
        # 显示回答
        answer = result.get('answer', result.get('response', ''))
        if answer:
            print(f"{Colors.BOLD}📖 生成的小说:{Colors.NC}\n")
            print("-" * 60)
            print(answer)
            print("-" * 60)
        else:
            print(f"{Colors.YELLOW}⚠ 未收到小说内容{Colors.NC}")
        
        print(f"\n{Colors.GREEN}✓ 生成完成！{Colors.NC}\n")
        
    except Exception as e:
        print(f"{Colors.RED}错误: {e}{Colors.NC}")


def main():
    parser = argparse.ArgumentParser(
        description="赛马娘同人文生成客户端",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互模式（非流式）
  python -m src.umamusume_novel.client.cli
  
  # 交互模式（流式）
  python -m src.umamusume_novel.client.cli --stream
  
  # 单次问答（非流式）
  python -m src.umamusume_novel.client.cli -q "写一篇关于米浴的故事"
  
  # 单次问答（流式）
  python -m src.umamusume_novel.client.cli --stream -q "写一篇关于米浴的故事"
        """
    )
    parser.add_argument(
        "-u", "--server-url",
        type=str,
        default="http://127.0.0.1:1111",
        help="后端服务地址，默认 http://127.0.0.1:1111"
    )
    parser.add_argument(
        "-q", "--question",
        type=str,
        help="直接提问并退出（非交互模式）"
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="使用流式模式（实时显示生成内容）"
    )

    args = parser.parse_args()

    # 初始化客户端
    client = UmamusumeClient(server_url=args.server_url)
    
    # 欢迎信息
    print(f"\n{Colors.BOLD}{'='*60}{Colors.NC}")
    print(f"{Colors.BOLD}{'  赛马娘同人文助手':^56}{Colors.NC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.NC}")
    print(f"\n模式: {Colors.CYAN}{'流式' if args.stream else '非流式'}{Colors.NC}")
    print(f"服务器: {Colors.CYAN}{args.server_url}{Colors.NC}")
    print(f"\n命令:")
    print(f"  • 输入问题开始生成")
    print(f"  • 输入 'exit' 或 'quit' 退出")
    print(f"  • 输入 'mode' 切换流式/非流式模式")
    print(f"{Colors.BOLD}{'='*60}{Colors.NC}\n")

    # 单次问答模式
    if args.question:
        if args.stream:
            handle_question_stream(client, args.question)
        else:
            handle_question_normal(client, args.question)
        return

    # 交互模式
    stream_mode = args.stream
    
    while True:
        try:
            user_input = input(f"{Colors.BOLD}You:{Colors.NC} ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print(f"\n{Colors.GREEN}再见！{Colors.NC}\n")
                break
            
            elif user_input.lower() == "mode":
                stream_mode = not stream_mode
                print(f"\n{Colors.CYAN}已切换到 {'流式' if stream_mode else '非流式'} 模式{Colors.NC}\n")
                continue
            
            elif not user_input:
                continue
            
            # 处理问题
            if stream_mode:
                handle_question_stream(client, user_input)
            else:
                handle_question_normal(client, user_input)

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{Colors.GREEN}再见！{Colors.NC}\n")
            break
        except Exception as e:
            print(f"\n{Colors.RED}错误: {e}{Colors.NC}\n")
            continue


if __name__ == "__main__":
    main()