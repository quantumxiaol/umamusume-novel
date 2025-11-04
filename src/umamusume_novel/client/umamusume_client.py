import requests
import json
from typing import Callable, Optional, Dict, Any


def ask_question(question: str, server_url: str) -> Dict[str, Any]:
    """
    向本地服务发送问题并获取回答（非流式）。

    :param question: 用户问题
    :param server_url: 服务端地址，如 http://127.0.0.1:1145/ask
    :return: 回答字典，包含 answer 等字段
    """
    payload = {"question": question}
    try:
        response = requests.post(server_url, json=payload, timeout=600)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {e}"}


def ask_question_stream(
    question: str, 
    server_url: str,
    callback: Callable[[str, str], None]
) -> None:
    """
    向本地服务发送问题并以流式方式获取回答。

    :param question: 用户问题
    :param server_url: 服务端地址，如 http://127.0.0.1:1145/askstream
    :param callback: 回调函数，接收 (event, data) 两个参数
    """
    payload = {"question": question}
    try:
        response = requests.post(
            server_url, 
            json=payload, 
            stream=True,
            timeout=600
        )
        
        if response.status_code != 200:
            callback('error', f"HTTP {response.status_code}: {response.text}")
            return
        
        # 处理流式响应
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            
            try:
                data = json.loads(line)
                event = data.get('event', 'unknown')
                event_data = data.get('data', '')
                callback(event, event_data)
            except json.JSONDecodeError as e:
                callback('error', f"JSON decode error: {e}")
    
    except requests.RequestException as e:
        callback('error', f"Request failed: {e}")

    
class UmamusumeClient:
    """
    赛马娘同人文生成客户端，支持流式和非流式两种模式。
    """

    def __init__(self, server_url: str = "http://127.0.0.1:1111"):
        """
        初始化客户端。
        
        :param server_url: 服务器基础地址，默认 http://127.0.0.1:1111
        """
        self.server_url = server_url.rstrip('/')
        self.ask_url = f"{self.server_url}/ask"
        self.askstream_url = f"{self.server_url}/askstream"

    def chat(self, user_input: str) -> Dict[str, Any]:
        """
        发送消息并返回 AI 回答（非流式）。

        :param user_input: 用户输入
        :return: 回答字典
        """
        return ask_question(user_input, self.ask_url)

    def chat_stream(self, user_input: str, callback: Callable[[str, str], None]) -> None:
        """
        发送消息并以流式方式接收 AI 回答。

        :param user_input: 用户输入
        :param callback: 回调函数，接收 (event, data) 两个参数
        """
        ask_question_stream(user_input, self.askstream_url, callback)