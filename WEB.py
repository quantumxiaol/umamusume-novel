from langchain_community.document_loaders import WebBaseLoader
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# 设置代理
proxies = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY'),
}

# 创建一个带有代理配置的 requests Session
session = requests.Session()
session.proxies.update(proxies)

def get_urls(web_file_path: str):
    urls = []
    with open(web_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    return urls