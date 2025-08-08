"""
python -m src.umamusume_novel.client.cli -u http://127.0.0.1:1111/ask
python -m src.umamusume_novel.client.cli -u http://127.0.0.1:1111/ask -q "写一篇爱慕织姬的甜甜同人文"
"""

import argparse
from .umamusume_client import UmamusumeClient

def main():
    parser = argparse.ArgumentParser(description="赛马娘同人文生成客户端")
    parser.add_argument(
        "-u", "--server-url",
        type=str,
        default="http://127.0.0.1:1145/ask",
        help="后端服务地址，默认 http://127.0.0.1:1145/ask"
    )
    parser.add_argument(
        "-q", "--question",
        type=str,
        help="直接提问并退出（非交互模式）"
    )

    args = parser.parse_args()

    client = UmamusumeClient(server_url=args.server_url)

    print("赛马娘同人文助手已启动！输入 'exit' 退出，'clear' 清除历史。\n")

    if args.question:
        # 非交互模式
        response = client.chat(args.question)
        print(f"Bot: {response}")
        return

    # 交互模式
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("再见！")
                break
            elif user_input.lower() == "clear":
                client.clear_history()
                print("Bot: 对话历史已清除。")
                continue
            elif not user_input:
                continue

            response = client.chat(user_input)
            print(f"Bot: {response}")

        except (KeyboardInterrupt, EOFError):
            print("\n再见！")
            break

if __name__ == "__main__":
    main()