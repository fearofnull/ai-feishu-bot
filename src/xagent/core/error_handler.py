"""
错误处理器模块

提供统一的错误处理机制
"""
import logging
from typing import Optional, Callable, Any
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """错误类别"""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    VALIDATION = "validation"
    EXECUTION = "execution"
    ROUTING = "routing"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class ErrorHandler:
    """错误处理器
    
    提供统一的错误处理机制：
    1. 错误分类
    2. 用户友好的错误消息
    3. 错误恢复策略
    """
    
    ERROR_MESSAGES = {
        ErrorCategory.NETWORK: "网络连接失败，请稍后重试",
        ErrorCategory.AUTHENTICATION: "认证失败，请检查 API Key 配置",
        ErrorCategory.RATE_LIMIT: "请求频率超限，请稍后重试",
        ErrorCategory.VALIDATION: "输入参数无效，请检查消息格式",
        ErrorCategory.EXECUTION: "执行过程中发生错误",
        ErrorCategory.ROUTING: "无法找到合适的执行器",
        ErrorCategory.CONFIGURATION: "配置错误，请检查系统配置",
        ErrorCategory.UNKNOWN: "发生未知错误",
    }
    
    RECOVERY_SUGGESTIONS = {
        ErrorCategory.NETWORK: "请检查网络连接后重试",
        ErrorCategory.AUTHENTICATION: "请使用 /config 命令检查 API Key 配置",
        ErrorCategory.RATE_LIMIT: "请等待几分钟后重试",
        ErrorCategory.VALIDATION: "请检查消息格式是否正确",
        ErrorCategory.EXECUTION: "请尝试简化消息或使用其他执行器",
        ErrorCategory.ROUTING: "请使用 @agent 或其他前缀指定执行器",
        ErrorCategory.CONFIGURATION: "请联系管理员检查系统配置",
        ErrorCategory.UNKNOWN: "请重试或联系管理员",
    }
    
    def __init__(self, message_sender=None):
        """初始化错误处理器
        
        Args:
            message_sender: 消息发送器（可选）
        """
        self.message_sender = message_sender
    
    def categorize_error(self, error: Exception) -> ErrorCategory:
        """分类错误
        
        Args:
            error: 异常对象
            
        Returns:
            错误类别
        """
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        if any(kw in error_str for kw in ["network", "connection", "timeout", "connect"]):
            return ErrorCategory.NETWORK
        
        if any(kw in error_str for kw in ["auth", "api key", "unauthorized", "forbidden", "401", "403"]):
            return ErrorCategory.AUTHENTICATION
        
        if any(kw in error_str for kw in ["rate limit", "too many", "429"]):
            return ErrorCategory.RATE_LIMIT
        
        if any(kw in error_str for kw in ["invalid", "validation", "format", "parse"]):
            return ErrorCategory.VALIDATION
        
        if any(kw in error_str for kw in ["route", "executor", "not found"]):
            return ErrorCategory.ROUTING
        
        if any(kw in error_str for kw in ["config", "setting"]):
            return ErrorCategory.CONFIGURATION
        
        if any(kw in error_type for kw in ["execution", "runtime"]):
            return ErrorCategory.EXECUTION
        
        return ErrorCategory.UNKNOWN
    
    def format_error_message(
        self,
        error: Exception,
        include_details: bool = True,
        include_suggestion: bool = True
    ) -> str:
        """格式化错误消息
        
        Args:
            error: 异常对象
            include_details: 是否包含详细错误信息
            include_suggestion: 是否包含恢复建议
            
        Returns:
            格式化后的错误消息
        """
        category = self.categorize_error(error)
        base_message = self.ERROR_MESSAGES.get(category, "发生错误")
        
        parts = [f"❌ {base_message}"]
        
        if include_details:
            parts.append(f"\n\n**详细信息**: {str(error)}")
        
        if include_suggestion:
            suggestion = self.RECOVERY_SUGGESTIONS.get(category, "")
            if suggestion:
                parts.append(f"\n\n**建议**: {suggestion}")
        
        return "".join(parts)
    
    def handle_error(
        self,
        error: Exception,
        chat_type: str = None,
        chat_id: str = None,
        message_id: str = None,
        log_error: bool = True
    ) -> str:
        """处理错误
        
        Args:
            error: 异常对象
            chat_type: 聊天类型（可选，用于发送消息）
            chat_id: 聊天 ID（可选，用于发送消息）
            message_id: 消息 ID（可选，用于发送消息）
            log_error: 是否记录错误日志
            
        Returns:
            格式化后的错误消息
        """
        if log_error:
            category = self.categorize_error(error)
            logger.error(f"[{category.value}] {error}", exc_info=True)
        
        error_message = self.format_error_message(error)
        
        if self.message_sender and chat_type and chat_id and message_id:
            try:
                self.message_sender.send_message(
                    chat_type, chat_id, message_id, error_message
                )
            except Exception as e:
                logger.error(f"Failed to send error message: {e}")
        
        return error_message


def handle_errors(func: Callable) -> Callable:
    """错误处理装饰器
    
    自动捕获异常并记录日志
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
    
    return wrapper


def safe_execute(func: Callable, default=None, *args, **kwargs) -> Any:
    """安全执行函数
    
    捕获所有异常并返回默认值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Safe execute failed: {e}")
        return default
