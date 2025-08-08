import requests
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory


from ..config import config
config.validate()

model_name=config.INFO_LLM_MODEL_NAME
api_key=config.INFO_LLM_MODEL_API_KEY
api_base=config.INFO_LLM_MODEL_BASE_URL

model = ChatOpenAI(
    model_name= model_name,
    api_key= api_key,
    base_url=api_base,
)

memory = ConversationBufferMemory()

def ask_question(question: str, server_url: str) -> str:
    """
    向本地服务发送问题并获取回答。

    :param question: 用户问题
    :param server_url: 服务端地址，如 http://127.0.0.1:1145/ask
    :return: 回答文本
    """
    payload = {"question": question}
    try:
        response = requests.post(server_url, json=payload)
        if response.status_code == 200:
            return response.json().get("answer", "")
        else:
            return f"Error: {response.status_code}, {response.text}"
    except requests.RequestException as e:
        return f"Request failed: {e}"
    
class UmamusumeClient:
    """
    赛马娘同人文生成客户端，支持带记忆的对话。
    """

    def __init__(self, server_url: str = "http://127.0.0.1:1145/ask"):
        self.server_url = server_url
        self.memory = ConversationBufferMemory()

    def chat(self, user_input: str) -> str:
        """
        发送消息并返回 AI 回答。

        :param user_input: 用户输入
        :return: AI 回答
        """
        # 构造历史对话
        history_msgs = self.memory.chat_memory.messages
        history_lines = []
        for msg in history_msgs:
            content = msg.content
            if isinstance(content, dict):
                content = content.get("content", "")
            elif not isinstance(content, str):
                content = str(content)
            history_lines.append(f"{msg.type.capitalize()}: {content}")
        history_str = "\n".join(history_lines)

        # 构造完整提示词
        full_prompt = f"""
你是一个助手，请根据以下历史对话和当前问题创作赛马娘同人文。

历史对话:
{history_str}

当前问题:
{user_input}
""".strip()

        # 调用服务
        answer = ask_question(full_prompt, self.server_url)

        # 更新记忆
        self.memory.chat_memory.add_user_message(user_input)
        self.memory.chat_memory.add_ai_message(answer)

        return answer

    def clear_history(self):
        """清空对话历史"""
        self.memory.chat_memory.clear()