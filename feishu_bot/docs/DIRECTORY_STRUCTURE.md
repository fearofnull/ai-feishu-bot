# Feishu Bot 目录结构说明

## 概览

```
feishu_bot/
├── __init__.py              # 包初始化文件
├── config.py                # 配置管理
├── feishu_bot.py           # 主应用类
├── models.py               # 数据模型定义
│
├── core/                   # 核心功能模块
│   ├── __init__.py
│   ├── event_handler.py    # 事件处理器
│   ├── executor_registry.py # 执行器注册表
│   ├── message_handler.py  # 消息处理器
│   ├── message_sender.py   # 消息发送器
│   ├── session_manager.py  # 会话管理器
│   ├── smart_router.py     # 智能路由器
│   └── websocket_client.py # WebSocket 客户端
│
├── executors/              # AI 执行器模块
│   ├── __init__.py
│   ├── ai_api_executor.py  # API 执行器基类
│   ├── ai_cli_executor.py  # CLI 执行器基类
│   ├── claude_api_executor.py   # Claude API 执行器
│   ├── claude_cli_executor.py   # Claude CLI 执行器
│   ├── gemini_api_executor.py   # Gemini API 执行器
│   ├── gemini_cli_executor.py   # Gemini CLI 执行器
│   └── openai_api_executor.py   # OpenAI API 执行器
│
├── utils/                  # 工具类模块
│   ├── __init__.py
│   ├── cache.py            # 缓存工具
│   ├── command_parser.py   # 命令解析器
│   ├── intent_classifier.py # 意图分类器
│   ├── response_formatter.py # 响应格式化器
│   └── ssl_config.py       # SSL 配置
│
└── docs/                   # 文档目录
    ├── CACHE_IMPLEMENTATION.md
    ├── DIRECTORY_STRUCTURE.md
    ├── EXECUTOR_REGISTRY.md
    ├── IMPLEMENTATION_STATUS.md
    ├── README.md
    ├── SSL_CONFIG_SUMMARY.md
    ├── WEBSOCKET_IMPLEMENTATION.md
    └── executor_config.example.json
```

## 模块说明

### 核心模块 (core/)

包含机器人的核心功能组件：

- **event_handler.py**: 处理飞书事件回调
- **executor_registry.py**: 管理所有 AI 执行器的注册和获取
- **message_handler.py**: 解析和处理飞书消息（文本、卡片、引用消息）
- **message_sender.py**: 发送消息到飞书
- **session_manager.py**: 管理用户会话和对话历史
- **smart_router.py**: 智能路由，根据命令选择合适的执行器
- **websocket_client.py**: WebSocket 连接管理

### 执行器模块 (executors/)

包含所有 AI 执行器实现：

- **ai_api_executor.py**: API 执行器抽象基类
- **ai_cli_executor.py**: CLI 执行器抽象基类
- **claude_api_executor.py**: Claude API 执行器
- **claude_cli_executor.py**: Claude Code CLI 执行器
- **gemini_api_executor.py**: Gemini API 执行器
- **gemini_cli_executor.py**: Gemini CLI 执行器
- **openai_api_executor.py**: OpenAI API 执行器

### 工具模块 (utils/)

包含各种工具类：

- **cache.py**: 消息去重缓存
- **command_parser.py**: 解析用户命令和 AI 提供商前缀
- **intent_classifier.py**: 使用 AI 分类用户意图
- **response_formatter.py**: 格式化机器人响应消息
- **ssl_config.py**: SSL 证书配置

### 文档目录 (docs/)

包含所有技术文档和示例配置文件。

## 导入示例

### 从外部导入

```python
from feishu_bot import FeishuBot
from feishu_bot.config import BotConfig
from feishu_bot.models import ExecutionResult, Message

# 导入核心模块
from feishu_bot.core import MessageHandler, SessionManager, SmartRouter

# 导入执行器
from feishu_bot.executors import GeminiCLIExecutor, ClaudeAPIExecutor

# 导入工具
from feishu_bot.utils import CommandParser, ResponseFormatter
```

### 模块内部导入

在 `feishu_bot` 包内部，使用绝对导入：

```python
# 在 core/smart_router.py 中
from feishu_bot.models import ParsedCommand
from feishu_bot.core.executor_registry import ExecutorRegistry
from feishu_bot.utils.command_parser import CommandParser

# 在 executors/gemini_cli_executor.py 中
from feishu_bot.executors.ai_cli_executor import AICLIExecutor
from feishu_bot.models import ExecutionResult
```

## 设计原则

1. **模块化**: 按功能将代码组织到不同的子包中
2. **清晰的职责**: 每个模块有明确的职责范围
3. **易于扩展**: 新增执行器或工具类只需在对应目录添加文件
4. **文档集中**: 所有文档统一放在 docs/ 目录
5. **绝对导入**: 使用绝对导入路径，避免相对导入的混淆

## 添加新功能

### 添加新的 AI 执行器

1. 在 `executors/` 目录创建新文件，如 `new_ai_executor.py`
2. 继承 `AIAPIExecutor` 或 `AICLIExecutor`
3. 在 `executors/__init__.py` 中导出
4. 在 `feishu_bot.py` 中注册

### 添加新的工具类

1. 在 `utils/` 目录创建新文件
2. 在 `utils/__init__.py` 中导出
3. 在需要的地方导入使用

### 添加新的核心功能

1. 在 `core/` 目录创建新文件
2. 在 `core/__init__.py` 中导出
3. 在 `feishu_bot.py` 中集成
