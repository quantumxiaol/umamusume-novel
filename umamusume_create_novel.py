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
from typing import TypedDict, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from starlette.middleware.cors import CORSMiddleware

from langchain.agents import  AgentExecutor
from langgraph.prebuilt import create_react_agent

from langchain.prompts import MessagesPlaceholder
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import AIMessage,ToolMessage
from dotenv import load_dotenv

rag_url = None
web_url = None

load_dotenv(".env")

model_name=os.getenv("INFO_LLM_MODEL_NAME")
api_key=os.getenv("INFO_LLM_MODEL_API_KEY")
api_base=os.getenv("INFO_LLM_MODEL_BASE_URL")

model_name_writer=os.getenv("WRITER_LLM_MODEL_NAME")
api_key_writer=os.getenv("WRITER_LLM_MODEL_API_KEY")
api_base_writer=os.getenv("WRITER_LLM_MODEL_BASE_URL")

ua=os.getenv("USER_AGENT")

# 初始化 LLM 模型
model = ChatOpenAI(
    model_name= model_name,
    api_key= api_key,
    base_url=api_base,
)
model_writer=ChatOpenAI(
    model_name= model_name_writer,
    api_key= api_key_writer,
    base_url=api_base_writer,
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

def extract_tool_info(agent_response):
    tool_calls = []
    tool_results = [] 

    for msg in agent_response["messages"]:
        # 判断消息类型
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls"):
            for tool_call in msg.tool_calls:
                tool_calls.append({
                "name": tool_call["name"],
                "arguments": tool_call["args"]
                })

        elif isinstance(msg, ToolMessage):
            tool_results.append({
            "id": msg.tool_call_id,
            "name": msg.name,
            "content": msg.content,
            "status": msg.status
            })

    # 提取最终回答
    final_answer = None
    for msg in reversed(agent_response["messages"]):
        if isinstance(msg, AIMessage):
            final_answer = msg.content  
        break

    return {
    "tool_calls": tool_calls,
    "tool_results": tool_results,
    "final_answer": final_answer
    }

# 定义请求模型
class QuestionRequest(BaseModel):
    question: str

# 定义响应模型
class AnswerResponse(BaseModel):
    answer: str


# 提供查询接口 http://127.0.0.1:1145/ask
@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    user_question = str(request.question) if request.question else ""
    print(f"用户问题：{user_question}")



    try:
        # 第一阶段：使用 RAG Agent 获取基础信息
        async with streamablehttp_client(rag_url) as (read_stream, write_stream, get_session_id):
        # print('MCP server连接成功')
            async with ClientSession(read_stream, write_stream) as session:

                await session.initialize()
                rag_tools = await load_mcp_tools(session)
                print("RAG可用MCP工具:", [tool.name for tool in rag_tools])

                rag_agent = create_react_agent(model, rag_tools)
                with open("./prompt/searchinrag.md", "r", encoding="utf-8") as file:
                    template = file.read()
                first_input = template.format(user_question=user_question)
                rag_result = await rag_agent.ainvoke({"messages": [HumanMessage(content=first_input)]})
                base_info = rag_result["messages"][-1].content
                result1 = extract_tool_info(rag_result)
                print(f"[第一阶段结果] 基础信息: {base_info}")
                print("\n[第一阶段Tool Call] : ", result1["tool_calls"])

        # 第二阶段：使用 Web Agent 结合基础信息回答问题
        async with streamablehttp_client(web_url) as (read_stream, write_stream, get_session_id):
        # print('MCP server连接成功')
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                web_tools = await load_mcp_tools(session)
                print("Web可用MCP工具:", [tool.name for tool in web_tools])

                web_agent = create_react_agent(model, web_tools)
                with open("./prompt/searchinweb.md", "r", encoding="utf-8") as file:
                    template = file.read()
                final_input = template.format(user_question=user_question,base_info=base_info)
                web_result = await web_agent.ainvoke(
                    {"messages": [HumanMessage(content=final_input)]},
                    config={"recursion_limit": 75}
                    )
                final_answer = web_result["messages"][-1].content
                result2 = extract_tool_info(web_result)
                print(f"[第二阶段结果] 最终回答: {final_answer}")
                print("\n[第二阶段Tool Call]: ", result2["tool_calls"])
                print("\n[第二阶段Tool Results]: ", result2["tool_results"])
                web_info=final_answer

                # return AnswerResponse(answer=final_answer)
            
        # 第三阶段：使用结合基础信息创作小说
        with open("./prompt/writenovel.md", "r", encoding="utf-8") as file:
            template = file.read()
        final_input = template.format(user_question=user_question,base_info=base_info,web_info=web_info)
        novel_agent = create_react_agent(model_writer,tools=[])
        result = await novel_agent.ainvoke({"messages": [HumanMessage(content=final_input)]})
        final_answer = result["messages"][-1].content
        print(" Final Answer:\n", final_answer)
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
    rag_url=args.rag_mcp_server_url
    web_url=args.web_mcp_server_url
    uvicorn.run(app, host="0.0.0.0", port=args.port,
                # reload=True
                )