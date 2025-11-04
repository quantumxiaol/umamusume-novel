#!/usr/bin/env python3
"""
赛马娘同人文客户端测试和使用示例

演示如何使用 UmamusumeClient 进行流式和非流式的小说生成
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.umamusume_novel.client.umamusume_client import UmamusumeClient


def example_normal_mode():
    """示例：非流式模式"""
    print("=" * 60)
    print("示例 1: 非流式模式")
    print("=" * 60)
    print()
    
    # 创建客户端
    client = UmamusumeClient(server_url="http://127.0.0.1:1111")
    
    # 发送问题
    question = "请写一篇关于米浴在雨中训练的短篇故事"
    print(f"问题: {question}\n")
    print("正在生成，请稍候...\n")
    
    # 获取结果
    result = client.chat(question)
    
    # 处理结果
    if 'error' in result:
        print(f"❌ 错误: {result['error']}")
    else:
        answer = result.get('answer', result.get('response', ''))
        print("✅ 生成完成！\n")
        print("-" * 60)
        print(answer)
        print("-" * 60)
    
    print()


def example_stream_mode():
    """示例：流式模式"""
    print("=" * 60)
    print("示例 2: 流式模式")
    print("=" * 60)
    print()
    
    # 创建客户端
    client = UmamusumeClient(server_url="http://127.0.0.1:1111")
    
    # 定义事件处理器
    class EventHandler:
        def __init__(self):
            self.novel_started = False
        
        def handle(self, event, data):
            if event == 'status':
                print(f"\r📍 状态: {data}", end='', flush=True)
            
            elif event == 'rag_result':
                print(f"\r✅ RAG 搜索完成，结果长度: {len(data)} 字符")
                print(f"   预览: {data[:100]}...\n")
            
            elif event == 'web_result':
                print(f"\r✅ Web 搜索完成，结果长度: {len(data)} 字符")
                print(f"   预览: {data[:100]}...\n")
            
            elif event == 'token':
                if not self.novel_started:
                    print(f"\r{' ' * 60}\r", end='')
                    print("\n📖 生成的小说:\n")
                    print("-" * 60)
                    self.novel_started = True
                print(data, end='', flush=True)
            
            elif event == 'done':
                if self.novel_started:
                    print()
                    print("-" * 60)
                print("\n✅ 生成完成！\n")
            
            elif event == 'error':
                print(f"\n❌ 错误: {data}\n")
    
    # 发送问题
    question = "请写一篇关于爱慕织姬在比赛前夕的短篇故事"
    print(f"问题: {question}\n")
    
    # 创建事件处理器
    handler = EventHandler()
    
    # 流式生成
    try:
        client.chat_stream(question, handler.handle)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消生成\n")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}\n")


def example_custom_handler():
    """示例：自定义事件处理"""
    print("=" * 60)
    print("示例 3: 自定义事件处理")
    print("=" * 60)
    print()
    
    # 创建客户端
    client = UmamusumeClient(server_url="http://127.0.0.1:1111")
    
    # 收集数据的处理器
    class DataCollector:
        def __init__(self):
            self.rag_result = ""
            self.web_result = ""
            self.novel_content = ""
            self.status_history = []
            self.error = None
        
        def handle(self, event, data):
            if event == 'status':
                self.status_history.append(data)
                print(f"[{len(self.status_history)}] {data}")
            elif event == 'rag_result':
                self.rag_result = data
            elif event == 'web_result':
                self.web_result = data
            elif event == 'token':
                self.novel_content += data
            elif event == 'error':
                self.error = data
        
        def print_summary(self):
            print("\n" + "=" * 60)
            print("生成摘要")
            print("=" * 60)
            print(f"✅ 经历阶段数: {len(self.status_history)}")
            print(f"✅ RAG 结果长度: {len(self.rag_result)} 字符")
            print(f"✅ Web 结果长度: {len(self.web_result)} 字符")
            print(f"✅ 小说长度: {len(self.novel_content)} 字符")
            
            if self.error:
                print(f"❌ 错误: {self.error}")
            
            print("\n阶段历史:")
            for i, status in enumerate(self.status_history, 1):
                print(f"  {i}. {status}")
            
            print("\n小说内容预览:")
            print("-" * 60)
            preview_len = min(200, len(self.novel_content))
            print(self.novel_content[:preview_len])
            if len(self.novel_content) > preview_len:
                print("...")
            print("-" * 60)
    
    # 发送问题
    question = "请写一篇关于特别周和无声铃鹿友谊的短篇故事"
    print(f"问题: {question}\n")
    print("正在生成...\n")
    
    # 创建收集器
    collector = DataCollector()
    
    # 流式生成
    try:
        client.chat_stream(question, collector.handle)
        collector.print_summary()
    except Exception as e:
        print(f"\n❌ 错误: {e}\n")


def main():
    """主函数"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "   赛马娘同人文客户端测试示例".center(56) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print()
    
    print("本示例将演示三种使用方式：")
    print("1. 非流式模式 - 等待完整结果")
    print("2. 流式模式 - 实时显示生成过程")
    print("3. 自定义处理 - 收集和分析数据")
    print()
    
    import time
    
    try:
        # 示例 1: 非流式模式
        print("按回车开始示例 1...")
        input()
        example_normal_mode()
        time.sleep(1)
        
        # 示例 2: 流式模式
        print("按回车开始示例 2...")
        input()
        example_stream_mode()
        time.sleep(1)
        
        # 示例 3: 自定义处理
        print("按回车开始示例 3...")
        input()
        example_custom_handler()
        
        print("\n" + "=" * 60)
        print("所有示例完成！")
        print("=" * 60)
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消\n")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

