# 端口配置说明

## 默认端口配置

赛马娘同人文生成系统使用以下默认端口：

| 服务 | 端口 | 说明 |
|------|------|------|
| **主服务器** | `1111` | 小说生成主服务，提供 `/ask` 和 `/askstream` 接口 |
| **RAG MCP** | `7777` | RAG 知识库检索服务 |
| **Web MCP** | `7778` | Web 搜索服务 |
| **前端开发服务器** | `5173` | Vue 前端开发服务器（开发模式） |

## 服务 URL

### 主服务器

- **非流式接口**: `http://127.0.0.1:1111/ask`
- **流式接口**: `http://127.0.0.1:1111/askstream`

### 客户端

客户端默认连接到主服务器：`http://127.0.0.1:1111`

```bash
# 使用默认端口
python -m src.umamusume_novel.client.cli

# 指定自定义端口
python -m src.umamusume_novel.client.cli -u http://127.0.0.1:8080
```

## 修改端口

### 方法 1：使用命令行参数

启动服务时可以指定自定义端口：

```bash
# 启动完整服务栈，自定义所有端口
python main.py server-only -rp 7777 -wp 7778 -sp 1111
```

参数说明：
- `-rp, --rag-port`: RAG MCP 端口
- `-wp, --web-port`: Web MCP 端口  
- `-sp, --server-port`: 主服务器端口

### 方法 2：修改代码中的默认值

编辑 `main.py`：

```python
DEFAULT_RAG_PORT = 7777
DEFAULT_WEB_PORT = 7778
DEFAULT_SERVER_PORT = 1111  # 主服务器端口
```

## 端口冲突

如果端口已被占用，会看到类似错误：

```
OSError: [Errno 48] Address already in use
```

### 解决方案

**1. 查看端口占用情况**

```bash
# macOS/Linux
lsof -i :1111
netstat -an | grep 1111

# 查看所有端口
lsof -i :1111 -i :7777 -i :7778
```

**2. 终止占用端口的进程**

```bash
# 查找并终止
lsof -ti :1111 | xargs kill -9

# 或使用停止脚本
./scripts/stop-server.sh
```

**3. 使用其他端口**

```bash
# 使用不同的端口启动
python main.py server-only -sp 8080
python -m src.umamusume_novel.client.cli -u http://127.0.0.1:8080
```

## 防火墙配置

如果需要从其他机器访问服务，需要：

1. **修改绑定地址**（从 `127.0.0.1` 改为 `0.0.0.0`）
2. **开放防火墙端口**

```bash
# macOS
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/python
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /path/to/python

# Linux (ufw)
sudo ufw allow 1111/tcp
sudo ufw allow 7777/tcp
sudo ufw allow 7778/tcp
```

⚠️ **安全提示**: 生产环境中应该：
- 使用反向代理（如 Nginx）
- 配置 HTTPS
- 添加身份验证
- 限制访问 IP

## 快速参考

### 检查服务是否运行

```bash
# 测试主服务器
curl http://127.0.0.1:1111/ask

# 测试 RAG MCP
curl http://127.0.0.1:7777/mcp

# 测试 Web MCP
curl http://127.0.0.1:7778/mcp
```

### 查看日志

```bash
# 查看主服务器日志
tail -f logs/server.log

# 查看 RAG MCP 日志
tail -f logs/rag_mcp.log

# 查看 Web MCP 日志
tail -f logs/web_mcp.log
```


