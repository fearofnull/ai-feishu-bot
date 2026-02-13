"""
Feishu AI Bot Package

飞书 AI 机器人包，提供与多个 AI 提供商集成的能力。
"""

__version__ = "1.0.0"

from .cache import DeduplicationCache
from .config import BotConfig
from .message_handler import MessageHandler
from .models import (
    ExecutionResult,
    Message,
    Session,
    ParsedCommand,
    ExecutorMetadata,
    MessageReceiveEvent,
)

__all__ = [
    "DeduplicationCache",
    "BotConfig",
    "MessageHandler",
    "ExecutionResult",
    "Message",
    "Session",
    "ParsedCommand",
    "ExecutorMetadata",
    "MessageReceiveEvent",
]
