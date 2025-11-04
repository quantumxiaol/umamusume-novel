# 前端 (Frontend)


## Environment

使用pnpm管理环境
```bash
# 安装pnpm(如果尚未安装)
npm install -g pnpm
pnpm --version

# 安装项目依赖
cd frontend
pnpm install

cat .env.template > .env

# 启动开发服务器
pnpm run dev

# 构建生产版本
pnpm run build
```

## Uasge
```bash

# 后端
python main.py server-only

# 前端
cd frontend
pnpm run dev

```

浏览器中打开默认地址`http://localhost:5173/`即可访问前端界面。

在文本输入框中输入你的创作指令，例如："请写一篇关于特别周努力训练，最终在比赛中获胜的故事，要体现她的坚持不懈。"

### 功能特性

#### 1. 流式模式
- 勾选"流式模式"复选框可启用实时流式生成
- 流式模式下可以实时看到生成进度
- 支持取消正在进行的生成

#### 2. RAG 和 Web 搜索结果展示
- 流式模式下会显示 RAG 搜索结果（本地知识库）
- 会显示 Web 搜索结果（在线搜索）
- 点击标题可以展开/折叠详细结果
- 显示结果字符数统计

#### 3. 实时状态提示
- 显示当前处理阶段（RAG 搜索、Web 搜索、小说生成）
- 实时显示生成进度

点击"生成小说"按钮，生成故事。


## 项目结构

        frontend/
        |- public/                    # 静态资源文件
        |   |- favicon.ico            # 网站图标
        |
        |- src/                       # 前端源代码根目录
        |   |- assets/                # 组件内使用的静态资源 (如图片、样式)
        |   |
        |   |- services/              # 封装与后端 API 交互的逻辑
        |   |   |- api.js             # API 请求函数
        |   |
        |   |- stores/                # Pinia 状态管理 stores
        |   |   |- novelStore.js      # 管理小说生成相关状态
        |   |
        |   |
        |   |- App.vue                # 根 Vue 组件
        |   |- main.js                # Vue 应用入口文件
        |
        |- index.html                 # 主页面 HTML 模板
        |- .env                       # 环境变量配置文件 
        |- .env.example               # 环境变量配置示例文件
        |- vite.config.js             # Vite 构建工具配置文件
        |- package.json               # 项目配置、依赖和脚本定义
        |- pnpm-lock.yaml             # pnpm 生成的依赖锁定文件
        |- README.md                  # 本前端子项目的说明文档