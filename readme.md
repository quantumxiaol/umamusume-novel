# 目的

要让LLM能够创作符合人设的赛马娘怪文书的同人文，有以下几种思路：

- 使用足够多的怪文书语料微调开源大模型
- 使用RAG的方式给LLM提供相关角色的人设
- 使用function call 的方法在LLM创作前先爬取相关的网页，包括角色设定、优秀的怪文书样例等

下面是使用RAG的方法进行怪文书写作的示例。

## ENV

conda

        conda create -n umamusume-novel python=3.12
        conda activate umamusume-novel
        pip install -r requirements.txt

uv

        uv venv --python 3.12
        use             source .venv/bin/activate
        or use          .venv/Scripts/activate
        uv sync

        playwright install

将.env.template复制为.env，修改其中的API_KEY。LLM，

我测试时使用QWEN，和OPENAI的格式是兼容的。如果要使用OPENAI，直接修改QWEN_MODEL_NAME等即可，不用管前缀和下面的OPENAI_API_KEY。

QWEN的API在[官网](https://bailian.console.aliyun.com/?tab=model#/model-market)中获取，免费也是有不少额度的。

## 运行

赛马娘基础知识问答

在终端1中运行`python umamusume_query.py -p 1122`开启服务器
在终端2中运行`python umamusume_client.py -u http://127.0.0.1:1122/ask`测试

赛马娘怪文书写作

使用RAG MCP先查询本地向量数据库的赛马娘的角色信息
使用WEB MCP在网络上查询赛马娘的角色信息

在终端1中运行`python raginfomcp.py -p 7778`开启Rag MCP服务器
在终端2中运行`python webinfomcp.py -p 7777`开启Web MCP服务器

在终端3运行

    python umamusume_create_novel.py -p 1111 \
        -w http://127.0.0.1:7777/mcp \
        -r http://127.0.0.1:7778/mcp

在终端4中运行`python umamusume_client.py -u http://127.0.0.1:1111/ask`测试

## 结果

[result](result.md)

## 概念

### ‌RAG（Retrieval Augmented Generation）

RAG‌是一种通过检索外部知识库来增强大语言模型 （LLM）生成能力的技术。RAG通过结合检索和生成两个阶段，使得模型能够根据用户的查询从知识库中检索相关信息，并据此生成更准确和相关的回答。
RAG的基本流程包括三个主要步骤：索引、检索和生成。在索引阶段，数据源被读取并分割成文档，然后通过向量存储嵌入。在检索阶段，模型根据用户的查询从知识库中检索相关文档。最后，在生成阶段，模型基于检索到的文档生成回答‌。

### Web Crawler

[Clawl4ai](https://github.com/unclecode/crawl4ai)提供为 LLM、AI Agent和数据管道量身定制的快速、AI 就绪的 Web 爬虫。Crawl4AI 开源、灵活且专为实时性能而构建，为开发人员提供无与伦比的速度、精度和部署便利性。