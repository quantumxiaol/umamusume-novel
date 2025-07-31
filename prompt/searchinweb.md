# 用户问题: 
{user_question}

# 基础信息
第一阶段使用RAG工具获取到的基础信息如下:
{base_info}

# 任务流程
你需要在网络上收集相关的资料。
你需要做如下事情:
- 对比RAG工具获取到的基础信息和原问题中涉及的内容，使用正确的角色信息，特别是正确的角色名称来进行搜索。
- 如果涉及到多个角色，请进行多次搜索。
- 请先使用 Web Crawler 工具查找与问题中涉及赛马娘角色的相关资料。
- 可以先使用web search工具搜索哔哩哔哩wiki（Bilibili wiki）和萌娘百科（moegirl wiki）。
- 使用web search工具分别对这些马娘用中文名称和日文名称进行搜索，不要使用英文名称进行搜索。
- 获得相关wiki的url后，使用crawler工具爬取该wiki的页面内容，按需选择代理工具，对于萌娘百科可能就需要代理。
- 你需要获取有关该角色的资料，包括但不限于角色设定、个人剧情、角色故事、角色原型生涯等。
- 在此阶段**不需要创作小说**，返回详细的资料即可。

# 输出
从网络上获取的相关角色的资料。

# 示例

用户创作和**马娘角色1**和**马娘角色2**的同人小说。

先使用web search的工具，在wiki上进行搜索，查询相关资料。

    query:"马娘角色1中文名称site:wiki.biligame.com/umamusume"
    query:"马娘角色1中文名称site:site:mzh.moegirl.org.cn"
    query:"马娘角色2中文名称site:wiki.biligame.com/umamusume"
    query:"马娘角色2中文名称site:site:mzh.moegirl.org.cn"

这将查询到相关角色的wiki的链接，注意分辨链接是否合理。

接着使用crawler去爬取这个结果链接，再汇总分析资料。

最后输出角色的资料，供下一阶段使用。