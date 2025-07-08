"""
Run
    Terminal 1:
    python webinfomcp.py -p 7777

    Terminal 2:
    python umamusume_create_novel.py -p 1111 -u http://127.0.0.1:7777/mcp

    Terminal 3:
    python umamusume_client.py -u http://127.0.0.1:1111/ask

curl -X POST http://127.0.0.1:1111/ask -H "Content-Type: application/json" \
-d '{"question":"帮我创作一篇爱慕织姬的甜甜的同人文，你可以先去wiki上搜索相关角色的信息，据此创作符合性格的同人小说"}'

curl -X POST http://localhost:1145/ask -json {"question": "请告诉我关于特别周的一些信息"}
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
description = """
这是一个关于赛马娘角色信息的表格，包含以下字段：
- 赛马娘中文名: 角色的中文名称
- 赛马娘英语名 / 日语名: 对应英文和日文名
- 生日: 出生日期
- 三围: BWH 尺寸
- 身高(cm): 单位厘米
- 声优(cv): 配音演员
- 赛马娘特殊称号(中文名/日语名): 特殊称号及日文名，也叫专属称号，或二つ名、别称
- 赛马娘特殊称号获取条件: 获取该称号的具体游戏内条件

例如：米浴的称号“漆黑刺客”的获取条件是：
重赏比赛出战23次以上，在人气第二以上的情况下取得菊花賞、天皇賞(春)的胜利；粉丝数达到320,000以上。
"""
metadata_doc = Document(page_content=description, metadata={"source": "table_description"})

# 加载文档,可换成PDF、txt、doc等其他格式文档
loader = CSVLoader('./docs/umamusume_character_baseinfo.csv', encoding='utf-8')
csv_documents = loader.load()
# for doc in csv_documents[:5]: 
#     print("-----")    
#     print(doc.page_content)
md_loader = TextLoader('./docs/umamusume_game_info.md', encoding='utf-8')
md_documents = md_loader.load()

# urls=get_urls('./docs/web_lists.txt')
# loader = WebBaseLoader(urls, proxies=proxies) 
# web_documents = loader.load()

# documents = [metadata_doc] + csv_documents + md_documents + web_documents
documents = [metadata_doc] + csv_documents + md_documents
# text_splitter = RecursiveCharacterTextSplitter.from_language(language="markdown", chunk_size=200, chunk_overlap=0)
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0,separators=["\n\n", "\n", "。", "，", " ", ""])
separators=["\n", "。", "，", " ", ""]
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    length_function=len,
    add_start_index=True,
    separators=separators,
)


pages = text_splitter.split_documents(md_documents)

# 加载PDF
# loader = PyMuPDFLoader("")
# pages = loader.load_and_split()


docs = text_splitter.create_documents(
    [page.page_content for page in pages]
)

texts=[metadata_doc] + csv_documents+docs

# print(f"共切分了 {len(texts)} 个文档块")
# for i, text in enumerate(texts[:3]):
#     print(f"第 {i} 个文本内容: {text.page_content[:100]}...")  # 打印前100字符

# 选择向量模型，并灌库
# oa_embeddings = QwenEmbeddings(
#     model="text-embedding-ada-002",
#     api_key=open_api_key,
#     base_url=openai_api_base,
# )


hf_embedding_model = HuggingFaceEmbeddings(
    model_name=os.getenv("HF_Embedding_Model"),
    # model_name="Qwen/Qwen3-Embedding-0.6B",
    model_kwargs = {'device': 'cpu'},
    encode_kwargs = {'normalize_embeddings': True}
    )
db = FAISS.from_documents(texts, hf_embedding_model)


# 获取检索器，选择 top-2 相关的检索结果
retriever = db.as_retriever(search_kwargs={"k": 10})

# 创建RAG工具
def rag_search(query: str) -> str:
    # docs = retriever.get_relevant_documents(query)
    docs = retriever.invoke(query)
    return "\n".join([doc.page_content for doc in docs])

class RagSearchTool(BaseTool):
    name: str = "rag_search"  # 添加类型注解
    description: str = "搜索本地知识库中的内容，用于获取赛马娘角色的基本信息。"

    def _run(self, query: str) -> str:
        docs = retriever.invoke(query)
        context = "\n".join([doc.page_content for doc in docs])
        return context  # 或者返回经过LLM处理后的结果

    async def _arun(self, query: str) -> str:
        # 如果需要异步支持，请确保retriever.invoke也支持异步
        return self._run(query)
# 创建带有 system 消息的模板
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的赛马娘同人文作家。
            你的任务是根据下述给定的已知信息创作小说。
            你应该先使用RAG检索本地的信息，获取准确的背景，
            再使用爬虫/搜索从网上获取额外的背景信息。
     
            请综合这些信息，从中提取角色背景、性格特点等，
            创作符合人物个性的故事。


            可用工具:
            {tool_names}

            工具描述:
            {tools}
    """),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])



# 构建 FastAPI 应用，提供服务
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
rag_tool = RagSearchTool()


# 全局变量保存 agent_executor
agent_executor = None

async def initialize_agent(args):
    global agent_executor
    MCP_SERVER_URL = args.mcp_server_url
    
    async with sse_client(MCP_SERVER_URL) as (read, write):
        print('MCP server连接成功')
        async with ClientSession(read, write) as session:
            await session.initialize()
            print('MCP server session已初始化')

            # 加载 MCP 工具
            mcp_tools = await load_mcp_tools(session)
            print("可用MCP工具:", [tool.name for tool in mcp_tools])

            # 添加我们自己的 RagTool
            tools = [rag_tool] + mcp_tools

            # 准备工具相关的变量
            tool_names = ", ".join([tool.name for tool in tools])
            tools_description = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])

            # 创建 Prompt Template 实例
            # formatted_prompt = prompt_template.format(
            #     tool_names=tool_names,
            #     tools=tools_description,
            #     history="",  # 这里可以根据实际情况填充
            #     input=""     # 这里可以根据实际情况填充
            # )

            # 创建 Agent
            agent = create_react_agent(llm=model, 
                                       tools=tools, 
                                       prompt=prompt_template,
                                       )
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            print("Agent 初始化完成")
            response = await agent_executor.ainvoke({
                "input": "请告诉我关于特别周的一些信息",
            })
            print(response)


# 提供查询接口 http://127.0.0.1:1145/ask
@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    if agent_executor is None:
        raise HTTPException(status_code=500, detail="Agent 未初始化，请先启动 MCP 连接")

    try:
        user_question = str(request.question) if request.question else ""
        print(f"用户问题：{user_question}")
        agent_scratchpad=[]
        # 使用 agent_executor 执行查询
        # result = await agent_executor.ainvoke({"input": user_question})
        result = await agent_executor.ainvoke({
            "input": user_question,
        })

        # 提取答案内容
        answer_text = result.get("output", "未能生成有效回答。")
        print(f"Agent 返回结果: {answer_text}")

        return AnswerResponse(answer=answer_text)
    except Exception as e:
        print(f"Error during processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    arg=argparse.ArgumentParser()
    arg.add_argument("--mcp_server_url","-u", type=str, default="http://127.0.0.1:7777/mcp")
    arg.add_argument("--port","-p", type=int, default=1111)
    args=arg.parse_args()
    loop = asyncio.get_event_loop()
    asyncio.run(initialize_agent(args))
    uvicorn.run(app, host="0.0.0.0", port=args.port,
                # reload=True
                )