from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from httplib2 import Http, ProxyInfo


if load_dotenv(".env")  :
    print("✅ 成功加载 .env 文件")
else:
    print("❌ 未能加载 .env 文件")
# "Google API key"
my_api_key = os.getenv("GOOGLE_API_KEY")
# "Custom Search Engine ID"
my_cse_id = os.getenv("GOOGLE_CSE_ID")
proxy_type=os.getenv("PROXY_TYPE")
proxy_host=os.getenv("PROXY_HOST")
proxy_port = int(os.getenv("PROXY_PORT"))

print("Search",my_cse_id)
print(f"🌐 使用代理：{proxy_type}://{proxy_host}:{proxy_port}")
if not all([my_api_key, my_cse_id, proxy_host, proxy_port]):
    raise ValueError("缺少必要的环境变量，请检查 .env 文件")

if proxy_type == "HTTP" or proxy_type == "http":
    proxy_type = 3  # httplib2 的 HTTP 代理类型
else:
    raise ValueError(f"Unsupported proxy type: {proxy_type}")

proxy_info = ProxyInfo(proxy_type=3,
                        proxy_host=proxy_host,
                        proxy_port=proxy_port)

# 创建带代理设置的 Http 实例
http = Http(proxy_info=proxy_info)


def extract_formatted_urls(results):
    """
    从 Google Custom Search API 的搜索结果中提取所有的 formattedUrl 字段。
    
    参数:
        results (list): 搜索结果列表，每个元素是一个字典（result item）
        
    返回:
        list: 包含 {'url': str, 'priority': int} 的字典列表
    """
    # return [item['formattedUrl'] for item in results if 'formattedUrl' in item]
    return [
        {'url': item['formattedUrl'], 'priority': idx + 1}
        for idx, item in enumerate(results)
        if 'formattedUrl' in item
    ]


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    # return res['items']
    return extract_formatted_urls(res.get('items', []))

# 使用代理发起 Google Custom Search 请求
def google_search_vai_proxy(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key, http=http)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    # return res.get('items', [])
    return extract_formatted_urls(res.get('items', []))

def google_search_urls(search_term:str,**kwargs):
    """
    use Google Custom Search API to search the web
    input:
    search_term: str
    output:
        list:  {'url': str, 'priority': int},
            where priority means the rank of the result,lower is better
    """
    service = build("customsearch", "v1", developerKey=my_api_key, http=http)
    res = service.cse().list(q=search_term, cx=my_cse_id, **kwargs).execute()
    if res.get('items', []) == []:
        raise ValueError("No results found")
    # return res.get('items', [])
    urls = extract_formatted_urls(res.get('items', []))
    return urls

def google_search_all(search_term:str,**kwargs):
    """
    use Google Custom Search API to search the web
    input:
    search_term: str
    output:
    result: results
    """
    service = build("customsearch", "v1", developerKey=my_api_key, http=http)
    res = service.cse().list(q=search_term, cx=my_cse_id, **kwargs).execute()
    if res.get('items', []) == []:
        raise ValueError("No results found")
    return res.get('items', [])