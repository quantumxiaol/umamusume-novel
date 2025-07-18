import asyncio
import os

from crawl4ai import AsyncWebCrawler
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter
from dotenv import load_dotenv
from urllib.parse import urljoin, quote
from crawl4ai.async_configs import ProxyConfig, CrawlerRunConfig
from bingsearch import search_bing

if load_dotenv(".env")  :
    print("✅ 成功加载 .env 文件")
else:
    print("❌ 未能加载 .env 文件")

class SingleProxyRotationStrategy:
    def __init__(self, proxy_config):
        self.proxy_config = proxy_config
    
    async def get_next_proxy(self):
        
        return self.proxy_config
    
# 创建单一代理配置
proxy_url = os.getenv("HTTP_PROXY") 
single_proxy = ProxyConfig(server=proxy_url)
md_generator = DefaultMarkdownGenerator(
    options={
        "ignore_links": True,
        "ignore_images": True,
        "escape_html": False,
        "body_width": 80
    }
)
prune_filter = PruningContentFilter(
    threshold=0.5,
    threshold_type="fixed",  # or "dynamic"
    min_word_threshold=50
)
# 使用单一代理配置初始化代理轮换策略
proxy_rotation_strategy = SingleProxyRotationStrategy(single_proxy)
crawler_config = CrawlerRunConfig(
    markdown_generator=md_generator,
    excluded_selector=".ads, .comments, #sidebar",
    )

crawler_config_proxy = CrawlerRunConfig(
    markdown_generator=md_generator,
    proxy_rotation_strategy=proxy_rotation_strategy,
    excluded_selector=".ads, .comments, #sidebar",
    )
async def _crawl_page(url):
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=url,config=crawler_config)
        return result.markdown

async def _crawl_page_proxy(url):
    print("Use Proxy URL",proxy_url)
    async with AsyncWebCrawler(verbose=True) as crawler:
        
        if proxy_url is None:
            result = await crawler.arun(url=url,config=crawler_config)
        else:
            result = await crawler.arun(url=url, config=crawler_config_proxy)
        return result.markdown
    


async def get_uma_info_on_bilibili_wiki(uma_name:str):
    """
    uma_name 爱慕织姬
    bilibi_wiki_url : https://wiki.biligame.com/umamusume/
    
    final_url : https://wiki.biligame.com/umamusume/%E7%88%B1%E6%85%95%E7%BB%87%E5%A7%AC

    craw; on final_url and return the markdown

    """
    encoded_name = quote(uma_name)
    base_bilibi_wiki_url = "https://wiki.biligame.com/umamusume/"
    final_url = urljoin(base_bilibi_wiki_url, encoded_name)
    # markdown = asyncio.run(_crawl_page_proxy(final_url))
    markdown = await _crawl_page(final_url)
    return markdown

async def get_uma_info_bing(uma_name:str,max_num_results:int=5):
    site=" site:wiki.biligame.com/umamusume/"
    result_dict=search_bing(uma_name+site,max_num_results)
    urls=[result['link'] for result in result_dict['results']]
    # markdowns=[asyncio.run(_crawl_page(url)) for url in urls]
    tasks = [_crawl_page(url) for url in urls]
    markdowns = await asyncio.gather(*tasks)
    return markdowns

"""
.moegirl.org.cn
moegirl.uk
"""