# 用户问题: 
{user_question}

# 基础信息
第一阶段使用RAG工具获取到的基础信息如下:
{base_info}

# 联网搜索到的信息
第二阶段使用搜索和爬虫得到的信息如下:
{web_info}

# 任务流程
你需要做如下事情:
- 请先分析用户的问题，确定小说的主人公（主要角色）；而有时会有多个角色出现。
- 请根据主人公（主要角色）的**基础信息**和**联网搜索到的信息**，确定主人公的角色形象。
- 使用RAG获取到的基础信息**没有必要全部出现**在小说正文中，特别是的赛马娘特殊称号获取条件（通常和原型生涯有关），仅作为角色人物信息的补充，这是同人小说而不是游戏指南。
- 使用WEB搜索到的信息要以角色剧情作为分析重点。
- 你需要从角色的准确资料以及获取的信息中分析**创建合理的角色形象**。
- 请根据用户问题，**创作符合需求的同人小说**，如果用户指定了情节按照用户指定的情节来，如果没有则自行根据性格编排合理的情节。
- 你可以根据角色的日语名称/英文名称联想到角色合理的昵称，小说中人物的称呼不能死板地保持官方名称一成不变，这又不是学术论文那么严谨。称呼要适当变化。比如角色“真机伶（Curren Chan,カレンチャン）”，就有“卡莲”、“卡莲酱”这样的昵称。再比如角色“爱慕织姬（Admire Vega,アドマイヤベガ）”，也有“爱织”、“阿雅贝”、“ayabe”这样的称呼。

# 剧情要点
请根据用户输入中对剧情的要求，结合人物性格，合理展开剧情。
大致上反应角色之间符合性格特征的互动（用户问题另有指定性格的除外）。

# 输出
返回符合要求，情节连贯，文笔流畅的同人小说。
字数（篇幅）符合要求，篇幅完整。
