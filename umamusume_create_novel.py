"""
Run
    Terminal 1:
    python webinfomcp.py -p 7777

    Terminal 2:
    python raginfomcp.py -p 7778    

    Terminal 3:
    (Linux MacOS)
    python umamusume_create_novel.py -p 1111 \
        -w http://127.0.0.1:7777/mcp \
        -r http://127.0.0.1:7778/mcp
    (Windows PS)
    python umamusume_create_novel.py -p 1111 `
            -w http://127.0.0.1:7777/mcp `
            -r http://127.0.0.1:7778/mcp    

    Terminal 4:
    python umamusume_client.py -u http://127.0.0.1:1111/ask

curl -X POST http://127.0.0.1:1111/ask -H "Content-Type: application/json" \
-d '{"question":"帮我创作一篇爱慕织姬的甜甜的同人文，你可以先去wiki上搜索相关角色的信息，据此创作符合性格的同人小说"}'

curl -X POST http://localhost:1122/ask -json {"question": "请告诉我关于特别周的一些信息"}
"""


import io
import os
import sys
import uvicorn
import json
import argparse
import asyncio

from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain_openai import OpenAI, ChatOpenAI
from openai import OpenAI as OpenAIClient
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.schema.runnable import RunnableSequence
from typing import TypedDict, List
from langgraph.prebuilt import create_react_agent
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dashscope import embeddings
from langchain_community.document_loaders import TextLoader,CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from starlette.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import PyMuPDFLoader
from langchain import hub
from langchain.schema import Document
from langchain_core.runnables import RunnableMap, RunnableLambda
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import BaseTool
from typing import Optional
from langchain.prompts import MessagesPlaceholder
from mcp.client.sse import sse_client
from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from dotenv import load_dotenv

from WEB import get_urls,proxies



load_dotenv(".env")

model=os.getenv("QWEN_MODEL_NAME")
api_key=os.getenv("QWEN_MODEL_API_KEY")
api_base=os.getenv("QWEN_MODEL_BASE_URL")

ua=os.getenv("USER_AGENT")

# 初始化 LLM 模型
model = ChatOpenAI(
    model_name= model,
    api_key= api_key,
    base_url=api_base,
)

app = FastAPI(title="LangChain-Umamusume-Server")

# 可选，前端报CORS时
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# 定义请求模型
class QuestionRequest(BaseModel):
    question: str

# 定义响应模型
class AnswerResponse(BaseModel):
    answer: str


# 全局变量保存 agent_executor
# 全局变量
agent_executor_rag = None
agent_executor_web = None

async def initialize_agent(rag_url,web_url):
    global agent_executor_rag
    global agent_executor_web
    rag_prompt = PromptTemplate.from_template(
        "请根据以下问题查询相关信息: {input}"
    )
    web_prompt = PromptTemplate.from_template(
        "基于以下背景信息回答问题: {input}"
    )
    # 初始化 RAG Agent
    async with sse_client(rag_url) as (read, write):
        print(f'RAG MCP 连接成功: {rag_url}')
        async with ClientSession(read, write) as session:
            await session.initialize()
            print(f'RAG MCP session已初始化')

            # 加载 RAG 工具
            rag_tools = await load_mcp_tools(session)
            print("RAG可用MCP工具:", [tool.name for tool in rag_tools])

            # 创建 RAG Agent
            rag_agent = create_react_agent(llm=model, tools=rag_tools,prompt=rag_prompt)
            agent_executor_rag = AgentExecutor(agent=rag_agent, tools=rag_tools, verbose=True)
            print("RAG Agent 初始化完成")

    # 初始化 Web Agent
    async with sse_client(web_url) as (read, write):
        print(f'Web MCP 连接成功: {web_url}')
        async with ClientSession(read, write) as session:
            await session.initialize()
            print(f'Web MCP session已初始化')

            # 加载 Web 工具
            web_tools = await load_mcp_tools(session)
            print("Web可用MCP工具:", [tool.name for tool in web_tools])

            # 创建 Web Agent
            web_agent = create_react_agent(llm=model, tools=web_tools,prompt=web_prompt)
            agent_executor_web = AgentExecutor(agent=web_agent, tools=web_tools, verbose=True)
            print("Web Agent 初始化完成")


# 提供查询接口 http://127.0.0.1:1145/ask
@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    if agent_executor_rag is None or agent_executor_web is None:
        raise HTTPException(status_code=500, detail="Agent 未初始化，请先启动 MCP 连接")

    try:
        user_question = str(request.question) if request.question else ""
        first_input = f"""
                请根据用户问题，先使用RAG查询本地的相关角色的信息：
                用户问题：{user_question}
                你返回角色的相关信息。
                """
        print(f"用户问题：{user_question}")

        # 第一阶段：使用 RAG Agent 获取基础信息
        rag_result = await agent_executor_rag.ainvoke({
            "input": first_input,
        })
        base_info = rag_result.get("output", "")
        print(f"[第一阶段结果] 基础信息: {base_info}")

        # 第二阶段：将原始问题 + 基础信息输入到 Web Agent
        final_input = f"""
        用户问题: {user_question}
        
        已知基础信息如下：
        {base_info}
        
        请结合上述信息和你的网络能力，给出更全面的回答。
        """
        web_result = await agent_executor_web.ainvoke({
            "input": final_input,
        })
        final_answer = web_result.get("output", "未能生成有效回答。")
        print(f"[第二阶段结果] 最终回答: {final_answer}")

        return AnswerResponse(answer=final_answer)

    except Exception as e:
        print(f"Error during processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    arg=argparse.ArgumentParser()
    arg.add_argument("-w","--web_mcp_server_url", 
                     type=str, 
                     default="http://127.0.0.1:7777/mcp",
                     help="Web MCP 服务器地址")
    arg.add_argument("-r","--rag_mcp_server_url", 
                     type=str, 
                     default="http://127.0.0.1:7778/mcp",
                     help="RAG MCP 服务器地址")
    arg.add_argument("-p","--port", type=int, default=1111)
    args=arg.parse_args()
    asyncio.run(initialize_agent(rag_url=args.rag_mcp_server_url,web_url=args.web_mcp_server_url))
    uvicorn.run(app, host="0.0.0.0", port=args.port,
                # reload=True
                )