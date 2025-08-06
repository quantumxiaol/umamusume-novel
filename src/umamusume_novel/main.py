import uvicorn
import argparse
from umamusume_novel.server.novel_generator import app

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
    app.state.web_mcp_url = args.web_mcp_server_url
    app.state.rag_mcp_url = args.rag_mcp_server_url
    uvicorn.run(app, host="0.0.0.0", port=args.port,
                # reload=True
                )