import os
import json
import asyncio
import traceback
from typing import AsyncGenerator, Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, AIMessageChunk
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools

from ..config import config

class NovelGenerationService:
    def __init__(self):
        # Load configuration
        self.model_name = config.INFO_LLM_MODEL_NAME
        self.api_key = config.INFO_LLM_MODEL_API_KEY
        self.api_base = config.INFO_LLM_MODEL_BASE_URL
        
        self.model_name_writer = config.WRITER_LLM_MODEL_NAME
        self.api_key_writer = config.WRITER_LLM_MODEL_API_KEY
        self.api_base_writer = config.WRITER_LLM_MODEL_BASE_URL
        
        self.searchinrag_prompt_path = os.path.join(config.PROMPT_DIRECTORY, "searchinrag.md")
        self.searchinweb_prompt_path = os.path.join(config.PROMPT_DIRECTORY, "searchinweb.md")
        self.writenovel_prompt_path = os.path.join(config.PROMPT_DIRECTORY, "writenovel.md")

        # Initialize LLMs
        self.model = ChatOpenAI(
            model_name=self.model_name,
            api_key=self.api_key,
            base_url=self.api_base,
        )
        self.model_writer = ChatOpenAI(
            model_name=self.model_name_writer,
            api_key=self.api_key_writer,
            base_url=self.api_base_writer,
        )

    def extract_tool_info(self, agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts tool calls and results from agent response."""
        tool_calls = []
        tool_results = [] 

        for msg in agent_response.get("messages", []):
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

        final_answer = None
        for msg in reversed(agent_response.get("messages", [])):
            if isinstance(msg, AIMessage):
                final_answer = msg.content  
                break

        return {
            "tool_calls": tool_calls,
            "tool_results": tool_results,
            "final_answer": final_answer
        }

    async def _execute_rag_stage(self, user_question: str, rag_url: str) -> str:
        """Executes the RAG search stage."""
        print(f"[Service] Starting RAG stage with URL: {rag_url}")
        async with streamablehttp_client(rag_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                rag_tools = await load_mcp_tools(session)
                print("[Service] RAG Tools:", [tool.name for tool in rag_tools])

                rag_agent = create_react_agent(self.model, rag_tools)
                with open(self.searchinrag_prompt_path, "r", encoding="utf-8") as file:
                    template = file.read()
                
                first_input = template.format(user_question=user_question)
                rag_result = await rag_agent.ainvoke({"messages": [HumanMessage(content=first_input)]})
                
                base_info = rag_result["messages"][-1].content
                
                # Log tool usage
                tool_info = self.extract_tool_info(rag_result)
                print(f"[Service] RAG Base Info len: {len(base_info)}")
                print(f"[Service] RAG Tool Calls: {tool_info['tool_calls']}")
                
                return base_info

    async def _execute_web_stage(self, user_question: str, base_info: str, web_url: str) -> str:
        """Executes the Web search stage."""
        print(f"[Service] Starting Web stage with URL: {web_url}")
        async with streamablehttp_client(web_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                web_tools = await load_mcp_tools(session)
                print("[Service] Web Tools:", [tool.name for tool in web_tools])

                web_agent = create_react_agent(self.model, web_tools)
                with open(self.searchinweb_prompt_path, "r", encoding="utf-8") as file:
                    template = file.read()
                
                final_input = template.format(user_question=user_question, base_info=base_info)
                web_result = await web_agent.ainvoke(
                    {"messages": [HumanMessage(content=final_input)]},
                    config={"recursion_limit": 75}
                )
                
                final_answer = web_result["messages"][-1].content
                
                # Log tool usage
                tool_info = self.extract_tool_info(web_result)
                print(f"[Service] Web Tool Calls: {tool_info['tool_calls']}")
                print(f"[Service] Web Tool Results: {tool_info['tool_results']}")

                return final_answer
    
    async def _execute_writer_stage_stream(self, user_question: str, base_info: str, web_info: str) -> AsyncGenerator[str, None]:
        """Executes the final novel writing stage with streaming."""
        with open(self.writenovel_prompt_path, "r", encoding="utf-8") as file:
            template = file.read()
        final_input = template.format(user_question=user_question, base_info=base_info, web_info=web_info)

        async for chunk in self.model_writer.astream([HumanMessage(content=final_input)]):
            content = ""
            if isinstance(chunk, AIMessageChunk):
                content = chunk.content
            elif hasattr(chunk, 'content'):
                content = chunk.content
            elif isinstance(chunk, dict) and 'content' in chunk:
                content = chunk['content']
            
            if content:
                yield content

    async def process_novel_generation_stream(self, user_question: str, rag_url: str, web_url: str) -> AsyncGenerator[str, None]:
        """Orchestrates the full generation process with streaming events."""
        try:
            # --- Stage 1: RAG ---
            yield json.dumps({"event": "status", "data": "Checking RAG database..."}, ensure_ascii=False) + "\n"
            base_info = await self._execute_rag_stage(user_question, rag_url)
            yield json.dumps({"event": "rag_result", "data": base_info}, ensure_ascii=False) + "\n"

            # --- Stage 2: Web Search ---
            yield json.dumps({"event": "status", "data": "Searching the web..."}, ensure_ascii=False) + "\n"
            web_info = await self._execute_web_stage(user_question, base_info, web_url)
            yield json.dumps({"event": "web_result", "data": web_info}, ensure_ascii=False) + "\n"

            # --- Stage 3: Writing ---
            yield json.dumps({"event": "status", "data": "Writing novel..."}, ensure_ascii=False) + "\n"
            async for chunk in self._execute_writer_stage_stream(user_question, base_info, web_info):
                yield json.dumps({"event": "token", "data": chunk}, ensure_ascii=False) + "\n"
            
            yield json.dumps({"event": "done", "data": ""}, ensure_ascii=False) + "\n"

        except asyncio.CancelledError:
            print("[Service] Generator cancelled")
            yield json.dumps({"event": "cancelled", "data": "Request cancelled"}, ensure_ascii=False) + "\n"
            return
        except Exception as e:
            traceback.print_exc()
            yield json.dumps({"event": "error", "data": str(e)}, ensure_ascii=False) + "\n"

    async def process_novel_generation(self, user_question: str, rag_url: str, web_url: str) -> str:
        """Sequential generation without streaming."""
        base_info = await self._execute_rag_stage(user_question, rag_url)
        web_info = await self._execute_web_stage(user_question, base_info, web_url)
        
        # Non-streaming writer call
        with open(self.writenovel_prompt_path, "r", encoding="utf-8") as file:
            template = file.read()
        final_input = template.format(user_question=user_question, base_info=base_info, web_info=web_info)
        
        result = await self.model_writer.ainvoke([HumanMessage(content=final_input)])
        return result.content
