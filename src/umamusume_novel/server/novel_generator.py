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


curl -X POST "http://127.0.0.1:1111/askstream" \
     -H "Content-Type: application/json" \
     -d '{"question": "请创作赛马娘米浴和训练员的感人故事"}'

"""


import io
import os
import sys
import uvicorn
import json
import argparse
import asyncio
import traceback

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from ..config import config
from .novel_service import NovelGenerationService

# Initialize Config
config.validate()

# Initialize Service
novel_service = NovelGenerationService()

app = FastAPI(title="LangChain-Umamusume-Server")

# 前端报CORS时
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


# 提供创作接口 http://127.0.0.1:1145/ask
@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: Request, user_request: QuestionRequest):
    user_question = str(user_request.question) if user_request.question else ""
    print(f"用户问题：{user_question}")

    rag_url = request.app.state.rag_mcp_url
    web_url = request.app.state.web_mcp_url

    # --- 可选：添加防御性检查 ---
    if not rag_url or not web_url:
        error_msg = "MCP server URLs are not configured. Please start the server with -r and -w arguments."
        print(f"[ERROR] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    
    try:
        final_answer = await novel_service.process_novel_generation(user_question, rag_url, web_url)
        print(" Final Answer:\n", final_answer)
        return AnswerResponse(answer=final_answer)

    except Exception as e: 
        # --- 打印详细的错误信息 ---
        error_msg = f"[ERROR] Unhandled error during processing in /ask route: {type(e).__name__}: {e}"
        print(error_msg)
        
        # --- 打印完整的堆栈跟踪 ---
        traceback_str = traceback.format_exc()
        print(f"[ERROR] Full Traceback:\n{traceback_str}")
        
        detailed_error = f"{str(e)}\n(See server logs for full traceback)" 
        raise HTTPException(status_code=500, detail=detailed_error)


@app.post("/askstream")
async def ask_question_stream(request: Request, user_request: QuestionRequest):
    user_question = str(user_request.question) if user_request.question else ""
    print(f"[STREAM] 用户问题：{user_question}")

    rag_url = request.app.state.rag_mcp_url
    web_url = request.app.state.web_mcp_url

    if not rag_url or not web_url:
        raise HTTPException(status_code=500, detail="MCP server URLs not configured.")

    async def event_stream():
        try:
             async for event in novel_service.process_novel_generation_stream(user_question, rag_url, web_url):
                 yield event

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"[STREAM ERROR] {error_msg}")
            traceback_str = traceback.format_exc()
            print(f"[STREAM ERROR] Full Traceback:\n{traceback_str}")
            yield json.dumps({"event": "error", "data": error_msg}, ensure_ascii=False) + "\n"

    # 返回流式响应
    return StreamingResponse(event_stream(), media_type="text/event-stream")
