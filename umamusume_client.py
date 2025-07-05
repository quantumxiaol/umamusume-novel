import requests
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough

import os,sys

from dotenv import load_dotenv
load_dotenv()

model=os.getenv("QWEN_MODEL_NAME")
api_key=os.getenv("QWEN_MODEL_API_KEY")
api_base=os.getenv("QWEN_MODEL_BASE_URL")
# 初始化记忆对象
memory = ConversationBufferMemory()
llm = ChatOpenAI(
    model_name= model,
    api_key= api_key,
    base_url=api_base,
)
# 设置服务端地址
url = "http://127.0.0.1:1145/ask"

def ask_question(question: str):
    """
    发送问题到服务端，并获取回答。
    
    :param question: 用户提出的问题
    :return: 服务端返回的回答
    """
    payload = {
        "question": question
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, json=payload)
        
        # 检查响应状态码
        if response.status_code == 200:
            answer = response.json().get("answer")
            # print(f"Answer: {answer}")
            return answer or ""
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"Request failed: {e}")
# 构建 Prompt 模板（用于包装用户问题 + 历史记录）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个对话机器人助手。请根据以下历史对话和当前问题给出回答。\n\n历史对话:\n{history}\n\n当前问题:\n{input}"),
    ("user", "{input}")
])

# 创建处理链：将 prompt 格式化后传给 ask_question 函数（模拟LLM）
def format_and_query(input_dict):
    formatted_prompt = prompt.invoke(input_dict)
    messages = formatted_prompt.to_messages()
    
    # 提取用户问题
    user_input = input_dict["input"]
    
    # 提取历史记录并构造上下文
    history = "\n".join([f"{msg.type}: {msg.content}" for msg in input_dict["history"]])
    full_prompt = f"历史对话:\n{history}\n\n当前问题:\n{user_input}"
    
    # 调用远程服务
    answer = ask_question(full_prompt)
    
    return answer

chain = (
    {
        "input": lambda x: x["input"],
        "history": lambda _: memory.chat_memory.messages,
    }
    | RunnablePassthrough.assign(context=format_and_query)
)

if __name__ == "__main__":
    print("开始对话！输入 'exit' 退出。\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # 添加用户输入到记忆
        memory.chat_memory.add_user_message(user_input)

        # 调用链
        result = chain.invoke({"input": user_input})

        # 获取回答（这里取决于如何封装结果）
        answer = result.get("context", "没有收到回答。")

        # 添加 AI 回答到记忆
        memory.chat_memory.add_ai_message(answer)

        print(f"Bot: {answer}")
