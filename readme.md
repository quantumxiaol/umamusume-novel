# 目的

使用RAG增强LLM的能力。

        pip install chromadb
        pip install faiss-cpu
        pip install sentence-transformers

## 运行

赛马娘基础知识问答

在终端1中运行`python ./umamusume_query.py`开启服务器
在终端2中运行`python ./umamusume_client.py`测试

赛马娘怪文书写作

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
