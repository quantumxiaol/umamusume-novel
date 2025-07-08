"""
Search And Crawl MCP Server

python webinfomcp.py -p 7777
to activate the MCP server

"""

import asyncio
from crawl4ai import AsyncWebCrawler

import os
import sys
import argparse
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from crawlonweb import get_uma_info_bing,get_uma_info_on_bilibili_wiki

load_dotenv()

app = FastAPI(title="Search MCP",
                description=""" 
                search and crawl,
                search umamusume information on bilibili wiki,
                search umamusume information on bing,
                crawl from url and return the result as markdown
                """,
                version="0.1.0")

@app.post("/bilibili_wiki", 
          description="""
          get umamusume info from bilibili wiki
          Crawl a page from url and return the result as markdown
          """,
)
def bilibili_wiki(uma_name:str):
    markdown = get_uma_info_on_bilibili_wiki(uma_name)
    return markdown

@app.post("/bing", 
          description="""
          get umamusume info from bing
          Crawl a page from url and return the result as markdown
          """,
)
def bing(uma_name:str):
    markdown = get_uma_info_bing(uma_name)
    return markdown

mcp = FastApiMCP(app)
mcp.mount(mount_path="/mcp")

if __name__ == "__main__":
    # uvicorn.run("mcpserver:app", host="0.0.0.0", port=8080, reload=True)
    # for route in app.routes:
    #     print(route.path)
    arg=argparse.ArgumentParser()
    
    arg.add_argument("--port","-p", type=int, default=7777)
    args=arg.parse_args()

    print(f"🚀 Starting server on port {args.port}")

    uvicorn.run("webinfomcp:app", host="0.0.0.0", port=args.port, reload=True)
    for route in app.routes:
        print(route.path)