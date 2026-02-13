# Feishu Bot Package

飞书 AI 机器人包，提供模块化、可扩展的架构，支持多个 AI 提供商和执行方式。

## 包结构

```
feishu_bot/
├── __init__.py              # 包初始化
├── config.py                # 配置管理（BotConfig 数据类）
├── cache.py                 # 消息去重缓存
├── message_handler.py       # 消息处理器
├── session_manager.py       # 会话管理器
├── command_parser.py        # 命令解析器
├── smart_router.py          # 智能路由器
├── executor_registry.py     # 执行器注册表
├── response_formatter.py    # 响应格式化器
├── message_sender.py        # 消息发送器
├── event_handler.py         # 事件处理器
├── websocket_client.py      # WebSocket 客户端
├── api_executors/           # AI API 执行器
│   ├── __init__.py
│   ├── base.py              # AIAPIExecutor 抽象基类
│   ├── claude_api.py        # Claude API 执行器
│   ├── gemini_api.py        # Gemini API 执行器
│   └── openai_api.py        # OpenAI API 执行器
├── cli_executors/           # AI CLI 执行器
│   ├── __init__.py
│   ├── base.py              # AICLIExecutor 抽象基类
│   ├── claude_cli.py        # Claude Code CLI 执行器
│   ├── gemini_cli.py        # Gemini CLI 执行器
│   └── temp_config.py       # 临时配置管理器
└── models.py                # 数据模型（ExecutionResult, Session, Message 等）
```

## 核心组件

### 配置管理 (config.py)

`BotConfig` 数据类支持从环境变量和 `.env` 文件加载配置，包括：
- 飞书应用配置
- AI API 密钥（Claude, Gemini, OpenAI）
- AI CLI 配置
- 会话管理配置
- 默认提供商和执行层设置

### 智能路由 (smart_router.py)

根据用户指令和消息内容自动选择最合适的 AI 执行方式：
- **API 层**：快速响应，适合一般问答
- **CLI 层**：深度代码能力，适合代码分析和文件操作

### 会话管理 (session_manager.py)

支持上下文连续对话：
- 自动创建和管理用户会话
- 持久化会话数据
- 支持会话命令（/new, /session, /history）
- 双层会话管理（飞书机器人会话 + AI CLI 原生会话）

## 使用示例

```python
from feishu_bot.config import BotConfig

# 加载配置
config = BotConfig.from_env()
config.validate()
config.print_status()

# 检查 API 密钥
if config.has_api_key("claude"):
    print("Claude API 已配置")
```

## 配置文件

参考 `.env.example` 文件创建 `.env` 配置文件。

## 扩展性

系统采用插件式架构，支持轻松添加新的 AI Agent：
1. 实现 `AIAPIExecutor` 或 `AICLIExecutor` 接口
2. 注册到 `ExecutorRegistry`
3. 添加命令前缀映射

详见设计文档。
