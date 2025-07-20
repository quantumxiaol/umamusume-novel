# 目的

要让LLM能够创作符合人设的赛马娘怪文书的同人文，有以下几种思路：

- 使用足够多的怪文书语料微调开源大模型
- 使用RAG的方式给LLM提供相关角色的人设，或者是优秀的范例
- 使用function call 的方法在LLM创作前先爬取相关的网页，包括角色设定、优秀的怪文书样例等

下面是使用 RAG+Web Crawler 的方法进行怪文书写作的示例。

## ENV

### OS

在Ubuntu、MacOS、WSL(Ubuntu)中进行过测试。在Windows上无法运行，因为crawl4ai所需的Playwright会出现问题。

### Proxy

使用http代理，因为赛马娘的萌娘百科通常需要使用代理才能访问。如果没有配置代理，将使用无代理的爬虫。

### Python 环境

使用[anaconda](https://www.anaconda.com/products/individual)或者[uv](https://github.com/astral-sh/uv)

conda

        conda create -n umamusume-novel python=3.12
        conda activate umamusume-novel
        pip install -r requirements.txt

uv

        uv venv --python 3.12
        source .venv/bin/activate
        uv sync

安装crawl4ai所需的浏览器

        playwright install

将.env.template复制为.env，修改其中的API_KEY。

我测试时使用的LLM为QWEN，和OPENAI的格式是兼容的。如果要使用OPENAI，直接修改QWEN_MODEL_NAME等即可，不用管前缀和下面的OPENAI_API_KEY。

QWEN的API在[官网](https://bailian.console.aliyun.com/?tab=model#/model-market)中获取，免费也是有不少额度的。

## 运行

### 赛马娘基础知识问答

在终端1中运行`python umamusume_query.py -p 1122`开启服务器
在终端2中运行`python umamusume_client.py -u http://127.0.0.1:1122/ask`测试

### 赛马娘怪文书写作

阶段1:
使用RAG MCP先查询本地向量数据库的赛马娘的角色信息,获得相对准确的信息,
阶段2:
使用WEB MCP在网络上查询赛马娘的角色信息,
阶段3:
根据这些信息去创作小说。

运行`source .venv/bin/activate`开启环境

在终端1中运行`bash run-server.sh`开启服务器

等待Web MCP 和 RAG MCP 启动成功，RAG使用本地的向量数据库，因此会比较慢。

在终端2中运行`bash run-client.sh`开启客户端

通过修改`run-param.sh`中的端口来修改配置。

在log文件中查看工具调用和服务器的输出。

## 结果

[Result](./results/result.md)工具调用的结果等

[Novel](./results/gen_novel.md)生成的一些同人小说

## 相关工具

### ‌RAG（Retrieval Augmented Generation）

RAG‌是一种通过检索外部知识库来增强大语言模型 （LLM）生成能力的技术。RAG通过结合检索和生成两个阶段，使得模型能够根据用户的查询从知识库中检索相关信息，并据此生成更准确和相关的回答。
RAG的基本流程包括三个主要步骤：索引、检索和生成。在索引阶段，数据源被读取并分割成文档，然后通过向量存储嵌入。在检索阶段，模型根据用户的查询从知识库中检索相关文档。最后，在生成阶段，模型基于检索到的文档生成回答‌。

### Web Crawler

[Clawl4ai](https://github.com/unclecode/crawl4ai)提供为 LLM、AI Agent和数据管道量身定制的快速、AI 就绪的 Web 爬虫。Crawl4AI 开源、灵活且专为实时性能而构建，为开发人员提供无与伦比的速度、精度和部署便利性。

## 项目结构

    umamusume-novel
        | |-.docs/                      # RAG所需的文档
        | |-.prompt/                    # Agent的prompt
        | |-.results/                   # 工具运行的一些结果，生成的一些怪文书的样例
        | |-.tests/                     # 一些测试用的python文件      
        | |-.env                        # 配置文件，需要自己配置key      
        | |-bingsearch.py               # Bing搜索
        | |-crawlonweb.py               # 爬虫
        | |-RAG.py                      # RAG
        | |-raginfomcp.py               # RAG MCP Server
        | |-readme.md
        | |-requirements_lock.txt       # 锁定的依赖项，包含了每个包准确的版本
        | |-requirements.txt
        | |-run-client.sh               # 运行客户端
        | |-run-param.sh                # 运行参数，可以修改MCP server的端口
        | |-run-server.sh               # 运行服务端，会先启动两个MCP server，再启动umamusume_create_novel.py
        | |-run.sh                      # 直接运行服务端+客户端
        | |-stop-server.sh              # 停止服务端
        | |-umamusume_client.py         # 客户端py
        | |-umamusume_create_novel.py   # 生成小说的服务端py
        | |-umamusume_query.py          # 赛马娘基础信息问答的py，开发过程中用于测试RAG是否正常
        | |-uv.lock                     # uv环境
        | |-WEB.py                      # Web 配置
        | |-webinfomcp.py               # Web MCP Server



## NOTICE
Disclaimer for Generated Content:

The software may generate content, output, or data as a result of its operation. The copyright holder provides no warranty, express or implied, regarding the accuracy, reliability, or suitability of such generated content. The use of the software and any content it generates is entirely at your own risk. The copyright holder shall not be liable for any damages, losses, or consequences arising from the use or misuse of the generated content.

关于生成内容的免责声明：

本软件在运行过程中可能生成内容、输出或数据。版权持有者对这些生成内容的准确性、可靠性或适用性不提供任何形式的担保。使用本软件及其生成内容的风险完全由使用者自行承担。版权持有者不对因使用或误用生成内容而造成的任何损害、损失或后果承担责任。