"""
Search And Crawl MCP Server

python webinfomcp.py --http -p 7777
to activate the MCP server

    playwright install


"""
import os
import asyncio
import sys
import argparse
import uvicorn
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

from crawlonweb import get_uma_info_bing,get_uma_info_on_bilibili_wiki
load_dotenv(".env")


mcp = FastMCP("Web Search MCP")


@mcp.tool(description="""
    get umamusume info from bilibili wiki
    Crawl a page from url and return the result as markdown
    Parameters:{uma_name: str}

""")
async def bilibili_wiki(uma_name:str):
    """"""
    try:
        markdown = await get_uma_info_on_bilibili_wiki(uma_name)
        return {
            "status":"success",
            "result":str(markdown)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }



@mcp.tool(description="""
    get umamusume info from web using bing,
    Crawl the result page from url and return the result as markdown
    Parameters:{uma_name: str}

""")
async def searchinbing(uma_name:str):
    """"""
    try:
        markdown = await get_uma_info_bing(uma_name)
        return {
            "status":"success",
            "result":str(markdown)
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
            port=args.port if args.port else 7777,
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()