from langchain_community.document_loaders import TextLoader, CSVLoader, PyMuPDFLoader
from langchain.embeddings.base import Embeddings
from dashscope.embeddings import TextEmbedding as DS_Embedding
import dashscope
from typing import List
import os
from dotenv import load_dotenv


load_dotenv(".env")


def load_all_documents_from_dir(directory):
    all_docs = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.endswith(".txt") or filename.endswith(".md"):
            loader = TextLoader(file_path, encoding='utf-8')
        elif filename.endswith(".csv"):
            loader = CSVLoader(file_path, encoding='utf-8')
        elif filename.endswith(".pdf"):
            loader = PyMuPDFLoader(file_path)
        else:
            continue  # 忽略不支持的格式

        docs = loader.load()
        all_docs.extend(docs)

    return all_docs


class QwenEmbeddings(Embeddings):
    def __init__(self, model_name: str = "text-embedding-v1", api_key: str = None):
        dashscope.api_key=os.getenv("DASH_SCOPE_API_KEY")
        self.model_name = model_name
        if api_key is None:
            api_key = os.getenv("QWEN_MODEL_API_KEY")
        if api_key:
            os.environ["DASHSCOPE_API_KEY"] = api_key
        self.api_key = api_key

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._get_embedding(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._get_embedding(text)

    def _get_embedding(self, text: str) -> List[float]:
        response = DS_Embedding.call(
            model=self.model_name,
            input=text
        )
        return response.output.text_embedding