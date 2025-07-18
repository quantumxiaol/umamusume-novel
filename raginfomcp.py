"""
RAG MCP
python raginfomcp.py --http -p 7778
to activate the MCP server

"""
import io
import os
import sys
import uvicorn
import json
import argparse
import uvicorn

from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain_openai import OpenAI, ChatOpenAI
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
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
import argparse
import uvicorn
import contextlib
from mcp.server import FastMCP
from collections.abc import AsyncIterator
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send
from mcp.server import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from dotenv import load_dotenv
from fastapi import FastAPI


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


pages = text_splitter.split_documents(documents)

# 加载PDF
# loader = PyMuPDFLoader("")
# pages = loader.load_and_split()


texts = text_splitter.create_documents(
    [page.page_content for page in pages]
)

# print(f"共切分了 {len(texts)} 个文档块")
# for i, text in enumerate(texts[:3]):
#     print(f"第 {i} 个文本内容: {text.page_content[:100]}...")  # 打印前100字符

# 选择向量模型，并灌库
# oa_embeddings = QwenEmbeddings(
#     model="text-embedding-ada-002",
#     api_key=open_api_key,
#     base_url=openai_api_base,
# )

# qw_embedding_model = QwenEmbeddings(
#     model_name="text-embedding-v2", 
#     api_key=os.getenv("QWEN_API_KEY"),
#     )

hf_embedding_model = HuggingFaceEmbeddings(
    model_name=os.getenv("HF_Embedding_Model"),
    model_kwargs = {'device': 'cpu'},
    encode_kwargs = {'normalize_embeddings': True}
    )
db = FAISS.from_documents(texts, hf_embedding_model)


# 获取检索器，选择 top-2 相关的检索结果
retriever = db.as_retriever(search_kwargs={"k": 10})

# 创建带有 system 消息的模板
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """你是一个对接问题排查机器人。
               你的任务是根据下述给定的已知信息回答用户问题。
               确保你的回复完全依据下述已知信息，不要编造答案。
               请用中文回答用户问题。

               已知信息:
               {context} """),
    ("user", "{question}")
])

# 自定义的提示词参数
chain_type_kwargs = {
    "prompt": prompt_template,
}

# 定义RetrievalQA链
qa_chain = RetrievalQA.from_chain_type(
    llm=model,
    chain_type="stuff",  # 使用stuff模式将上下文拼接到提示词中
    chain_type_kwargs=chain_type_kwargs,
    retriever=retriever
)


mcp = FastMCP("RAG Search MCP")


@mcp.tool(description="""
            Use Local Vector Database to answer questions about Umamusume characters.
            contain accurate and basic information about Umamusume characters.
            input: AnswerResponse
            Parameters:{question: str}
            output: AnswerResponse
            Example:{
                "question": "What is the birthday of Rice Shower?"
            }
            Result:{
                "answer": "Rice Shower was born on 3/05."
            }

""")

async def rag(question: str):
    try:
        # 获取用户问题
        user_question = question
        print(user_question)

        # 通过RAG链生成回答
        raw_answer = qa_chain.invoke(user_question)

        if isinstance(raw_answer, dict):
            answer_text = raw_answer.get("result", str(raw_answer))  # 提取 result 字段
        else:
            answer_text = raw_answer

        # 返回答案
        print(answer_text)
        return {
            "status":"success",
            "result":str(answer_text)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }        



def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    sse = SseServerTransport("/messages/")
    session_manager = StreamableHTTPSessionManager(
        app=mcp_server,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            print("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                print("Application shutting down...")

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/mcp", app=handle_streamable_http),
            Mount("/messages/", app=sse.handle_post_message),
        ],
        lifespan=lifespan,
    )


# Main entry point
def main():
    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description="Run Search and Crawl MCP server")

    parser.add_argument(
        "--http",
        action="store_true",
        help="Run the server with Streamable HTTP and SSE transport rather than STDIO (default: False)",
    )
    parser.add_argument(
        "--sse",
        action="store_true",
        help="(Deprecated) An alias for --http (default: False)",
    )
    parser.add_argument(
        "--host", default=None, help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port","-p", type=int, default=None, help="Port to listen on (default: 8887)"
    )
    args = parser.parse_args()
    print(f"🚀 Starting server on port {args.port}")
    use_http = args.http or args.sse

    if not use_http and (args.host or args.port):
        parser.error(
            "Host and port arguments are only valid when using streamable HTTP or SSE transport (see: --http)."
        )
        sys.exit(1)

    if use_http:
        starlette_app = create_starlette_app(mcp_server, debug=True)
        uvicorn.run(
            starlette_app,
            host=args.host if args.host else "127.0.0.1",
            port=args.port if args.port else 7778,
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()