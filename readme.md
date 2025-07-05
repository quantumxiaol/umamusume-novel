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

        uv venv --python 3.12.0
        uv sync


将.env.template复制为.env，修改其中的API_KEY。LLM，

我测试时使用QWEN，和OPENAI的格式是兼容的。如果要使用OPENAI，直接修改QWEN_MODEL_NAME等即可，不用管前缀和下面的OPENAI_API_KEY。

QWEN的API在[官网](https://bailian.console.aliyun.com/?tab=model#/model-market)中获取，免费也是有不少额度的。

## 运行

赛马娘基础知识问答

在终端1中运行`python ./umamusume_query.py`开启服务器
在终端2中运行`python ./umamusume_client.py`测试

赛马娘怪文书写作

在./docs/web_lists.txt中添加网站，一行一个，可以添加一些马娘的萌娘百科等网址，如果需要登录的网站抓不了。默认是通过本地代理访问的，因为大陆连不上萌娘百科。

在终端1中运行`python ./umamusume_create_novel.py`开启服务器
在终端2中运行`python ./umamusume_client.py`测试

## 结果

[result](result.md)

## 概念

### ‌RAG（Retrieval Augmented Generation）

RAG‌是一种通过检索外部知识库来增强大语言模型 （LLM）生成能力的技术。RAG通过结合检索和生成两个阶段，使得模型能够根据用户的查询从知识库中检索相关信息，并据此生成更准确和相关的回答。
RAG的基本流程包括三个主要步骤：索引、检索和生成。在索引阶段，数据源被读取并分割成文档，然后通过向量存储嵌入。在检索阶段，模型根据用户的查询从知识库中检索相关文档。最后，在生成阶段，模型基于检索到的文档生成回答‌。

### 加载过程

加载：通过文档加载器完成。langchain 提供了 html、csv、pdf 等诸多加载器。
拆分：文本拆分器将大型文档拆分成较小的块，大块数据更难搜索，并且不适合模型的有限上下文窗口。
存储：存储和索引拆分，以便以后可以搜索它们。通常使用 VectorStore 和 Embeddings 模型来完成。

### 检索和生成

检索：给定用户输入，使用检索器从存储中检索相关分割后的文档。
生成：ChatModel/LLM 使用包含问题和检索到的数据的提示词生成答案。

#### chroma

chromadb是一个开源的向量数据库，用于存储和检索向量数据。它使用 Faiss 作为底层的向量检索引擎，并支持多种数据类型，如文本、图像、音频等。

部分内容参照了http://wfcoding.com/articles/practice/0318/
以及https://github.com/Sbwillbealier/qa-rag-demo
