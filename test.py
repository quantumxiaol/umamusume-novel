from bingsearch import search_bing
import requests

query_str="爱慕织姬 site:wiki.biligame.com/umamusume/"

print(f"search in bing for {query_str}\n",search_bing(query=query_str))

from crawlonweb import get_uma_info_bing,get_uma_info_on_bilibili_wiki

print("Bing")

print(get_uma_info_bing("爱慕织姬"))

print("Bilibili wiki")

print(get_uma_info_on_bilibili_wiki("爱慕织姬"))