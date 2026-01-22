# src/umamusume_novel/config.py

from dotenv import load_dotenv
from typing import Optional
import os

# 加载 .env 文件（从项目根目录开始）
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

class Config:
    """
    配置类：集中管理所有环境变量
    """

    # ================== LLM Settings ==================
    # Info LLM (用于信息查询)
    INFO_LLM_MODEL_NAME: str = os.getenv("INFO_LLM_MODEL_NAME", "qwen-max-latest")
    INFO_LLM_MODEL_BASE_URL: str = os.getenv("INFO_LLM_MODEL_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    INFO_LLM_MODEL_API_KEY: str = os.getenv("INFO_LLM_MODEL_API_KEY", "")
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", INFO_LLM_MODEL_API_KEY)  # 兼容旧变量

    # Writer LLM (用于小说生成)
    WRITER_LLM_MODEL_NAME: str = os.getenv("WRITER_LLM_MODEL_NAME", "qwen-long-latest")
    WRITER_LLM_MODEL_BASE_URL: str = os.getenv("WRITER_LLM_MODEL_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    WRITER_LLM_MODEL_API_KEY: str = os.getenv("WRITER_LLM_MODEL_API_KEY", "")

    # 默认 User-Agent
    USER_AGENT: str = os.getenv("USER_AGENT", "MyApp/1.0")

    # ================Prompt Settings ==================
    # ================Prompt Settings ==================
    # Default to "prompt" directory in the same package as config.py
    _prompt_directory = os.getenv("PROMPT_DIRECTORY", "prompt")
    PROMPT_DIRECTORY:str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), _prompt_directory)
    )

    # ================== RAG Settings ==================
    HF_Embedding_Model: str = os.getenv("HF_Embedding_Model", "Qwen/Qwen3-Embedding-0.6B")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))

    # 注意：RAG_DIRECTORY 是相对路径，需转为绝对路径
    _rag_dir = os.getenv("RAG_DIRECTORY", "./resources/docs")
    RAG_DIRECTORY: str = os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), _rag_dir.lstrip("./"))
    )

    # ================== Proxy Settings ==================
    PROXY_TYPE: Optional[str] = os.getenv("PROXY_TYPE")  # http, socks5 等
    PROXY_HOST: Optional[str] = os.getenv("PROXY_HOST")
    PROXY_PORT: Optional[int] = int(os.getenv("PROXY_PORT", "0")) if os.getenv("PROXY_PORT") else None

    HTTP_PROXY: Optional[str] = os.getenv("HTTP_PROXY")
    HTTPS_PROXY: Optional[str] = os.getenv("HTTPS_PROXY")

    @classmethod
    def get_proxy_dict(cls) -> dict:
        """
        返回标准的 proxy 字典，可用于 requests 或 httpx
        """
        if cls.HTTP_PROXY and cls.HTTPS_PROXY:
            return {
                "http://": cls.HTTP_PROXY,
                "https://": cls.HTTPS_PROXY,
            }
        elif cls.PROXY_TYPE and cls.PROXY_HOST and cls.PROXY_PORT:
            scheme = f"{cls.PROXY_TYPE}://{cls.PROXY_HOST}:{cls.PROXY_PORT}"
            return {
                "http://": scheme,
                "https://": scheme,
            }
        return {}

    # ================== Google Search Settings ==================
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID: str = os.getenv("GOOGLE_CSE_ID", "")

    @classmethod
    def validate(cls):
        """
        验证必要配置是否已设置
        """
        missing = []
        if not cls.INFO_LLM_MODEL_API_KEY and not cls.DASHSCOPE_API_KEY:
            missing.append("INFO_LLM_MODEL_API_KEY or DASHSCOPE_API_KEY")
        if not cls.WRITER_LLM_MODEL_API_KEY:
            missing.append("WRITER_LLM_MODEL_API_KEY")
        if not cls.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        if not cls.GOOGLE_CSE_ID:
            missing.append("GOOGLE_CSE_ID")

        if missing:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

# 创建一个全局实例，方便导入
config = Config()