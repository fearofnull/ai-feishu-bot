# Feishu Bot Package

飞书 AI 机器人包，提供模块化、可扩展的架构，支持多个 AI 提供商和执行方式。

## 包结构

```
feishu_bot/
├── __init__.py              # 包初始化
├── config.py                # 配置管理（BotConfig 数据类）
├── feishu_bot.py           # 主应用类
├── models.py               # 数据模型（ExecutionResult, Session, Message 等）
│
├── core/                   # 核心功能模块
│   ├── event_handler.py    # 事件处理器
│   ├── executor_registry.py # 执行器注册表
│   ├── message_handler.py  # 消息处理器
│   ├── message_sender.py   # 消息发送器
│   ├── session_manager.py  # 会话管理器
│   ├── smart_router.py     # 智能路由器
│   └── websocket_client.py # WebSocket 客户端
│
├── executors/              # AI 执行器模块
│   ├── ai_api_executor.py  # API 执行器基类
│   ├── ai_cli_executor.py  # CLI 执行器基类
│   ├── claude_api_executor.py   # Claude API 执行器
│   ├── claude_cli_executor.py   # Claude CLI 执行器
│   ├── gemini_api_executor.py   # Gemini API 执行器
│   ├── gemini_cli_executor.py   # Gemini CLI 执行器
│   └── openai_api_executor.py   # OpenAI API 执行器
│
├── utils/                  # 工具类模块
│   ├── cache.py            # 消息去重缓存
│   ├── command_parser.py   # 命令解析器
│   ├── intent_classifier.py # 意图分类器
│   ├── response_formatter.py # 响应格式化器
│   └── ssl_config.py       # SSL 配置
│
└── docs/                   # 文档目录
    ├── DIRECTORY_STRUCTURE.md  # 详细的目录结构说明
    ├── README.md               # 本文件
    └── executor_config.example.json # 配置示例
```

详细的目录结构说明请参考 [DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md)。

## 核心组件

### 配置管理 (config.py)

`BotConfig` 数据类支持从环境变量和 `.env` 文件加载配置，包括：
- 飞书应用配置（app_id, app_secret）
- AI API 密钥（Claude, Gemini, OpenAI）
- AI CLI 配置（target_directory, timeout）
- 会话管理配置（storage_path, max_messages, timeout）
- 默认提供商和执行层设置

### 智能路由 (core/smart_router.py)

根据用户指令和消息内容自动选择最合适的 AI 执行方式：
- **API 层**：快速响应，适合一般问答
- **CLI 层**：深度代码能力，适合代码分析和文件操作

支持的命令前缀：
- `@claude-api`, `@claude` - Claude API
- `@gemini-api`, `@gemini` - Gemini API
- `@openai`, `@gpt` - OpenAI API
- `@claude-cli`, `@code` - Claude Code CLI
- `@gemini-cli` - Gemini CLI

### 会话管理 (core/session_manager.py)

支持上下文连续对话：
- 自动创建和管理用户会话
- 持久化会话数据到 JSON 文件
- 支持会话命令（`/new`, `/session`, `/history`）
- 双层会话管理（飞书机器人会话 + AI CLI 原生会话）

### 消息处理 (core/message_handler.py)

处理飞书消息的解析和组合：
- 支持文本消息和卡片消息
- 支持引用消息（quoted messages）
- 自动提取卡片消息内容
- 组合引用消息和当前消息

### 执行器注册表 (core/executor_registry.py)

管理所有 AI 执行器：
- 注册和获取 API/CLI 执行器
- 执行器元数据管理
- 可用性检查
- 支持从配置文件加载

## 使用示例

### 基本使用

```python
from feishu_bot.config import BotConfig
from feishu_bot.feishu_bot import FeishuBot

# 加载配置
config = BotConfig.from_env()
config.validate()

# 创建机器人实例
bot = FeishuBot(config)

# 启动机器人
bot.start()
```

### 检查配置

```python
from feishu_bot.config import BotConfig

# 加载配置
config = BotConfig.from_env()
config.validate()
config.print_status()

# 检查 API 密钥
if config.has_api_key("claude"):
    print("Claude API 已配置")
if config.has_api_key("gemini"):
    print("Gemini API 已配置")
```

### 使用执行器

```python
from feishu_bot.executors import GeminiCLIExecutor, ClaudeAPIExecutor

# 创建 CLI 执行器
gemini_cli = GeminiCLIExecutor(
    target_dir="/path/to/project",
    timeout=600
)

# 执行命令
result = gemini_cli.execute(
    "分析这个项目的代码结构",
    additional_params={"user_id": "user123"}
)

print(result.stdout)
```

## 配置文件

参考项目根目录的 `.env.example` 文件创建 `.env` 配置文件。

必需的配置项：
- `FEISHU_APP_ID` - 飞书应用 ID
- `FEISHU_APP_SECRET` - 飞书应用密钥

可选的配置项：
- `CLAUDE_API_KEY` - Claude API 密钥
- `GEMINI_API_KEY` - Gemini API 密钥
- `OPENAI_API_KEY` - OpenAI API 密钥
- `TARGET_DIRECTORY` - CLI 执行器的目标目录
- 更多配置项请参考 `.env.example`

## 扩展性

系统采用插件式架构，支持轻松添加新的 AI 执行器：

1. **添加新的 API 执行器**：
   - 在 `executors/` 目录创建新文件
   - 继承 `AIAPIExecutor` 基类
   - 实现 `execute()` 和 `get_provider_name()` 方法
   - 在 `feishu_bot.py` 中注册

2. **添加新的 CLI 执行器**：
   - 在 `executors/` 目录创建新文件
   - 继承 `AICLIExecutor` 基类
   - 实现必要的方法
   - 在 `feishu_bot.py` 中注册

3. **添加新的工具类**：
   - 在 `utils/` 目录创建新文件
   - 在 `utils/__init__.py` 中导出

详见 [DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md) 中的"添加新功能"章节。

## 群聊功能

机器人支持群聊，但只有在被 @ 时才会响应：
- 私聊：机器人会响应所有消息
- 群聊：只有 @ 机器人时才会响应

## 技术特性

- ✅ 模块化架构，职责清晰
- ✅ 支持多个 AI 提供商（Claude, Gemini, OpenAI）
- ✅ 支持 API 和 CLI 两种执行方式
- ✅ 智能路由，自动选择最佳执行器
- ✅ 会话管理，支持上下文对话
- ✅ 消息去重，避免重复处理
- ✅ 引用消息支持，包括卡片消息
- ✅ WebSocket 长连接，实时接收消息
- ✅ SSL 证书配置，安全通信
- ✅ 完善的错误处理和日志记录

## 许可证

请参考项目根目录的 LICENSE 文件。
