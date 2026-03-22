"""
ErrorHandler 单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock

from src.xagent.core.error_handler import ErrorHandler, ErrorCategory


class TestErrorHandler:
    """ErrorHandler 测试类"""
    
    @pytest.fixture
    def mock_message_sender(self):
        """创建模拟的消息发送器"""
        return Mock()
    
    @pytest.fixture
    def error_handler(self, mock_message_sender):
        """创建 ErrorHandler 实例"""
        return ErrorHandler(message_sender=mock_message_sender)
    
    def test_categorize_error_network(self, error_handler):
        """测试分类网络错误"""
        error = Exception("Network connection timeout")
        category = error_handler.categorize_error(error)
        assert category == ErrorCategory.NETWORK
    
    def test_categorize_error_authentication(self, error_handler):
        """测试分类认证错误"""
        error = Exception("Invalid API key or unauthorized")
        category = error_handler.categorize_error(error)
        assert category == ErrorCategory.AUTHENTICATION
    
    def test_categorize_error_rate_limit(self, error_handler):
        """测试分类速率限制错误"""
        error = Exception("Rate limit exceeded 429")
        category = error_handler.categorize_error(error)
        assert category == ErrorCategory.RATE_LIMIT
    
    def test_categorize_error_validation(self, error_handler):
        """测试分类验证错误"""
        error = Exception("Invalid format or validation failed")
        category = error_handler.categorize_error(error)
        assert category == ErrorCategory.VALIDATION
    
    def test_categorize_error_routing(self, error_handler):
        """测试分类路由错误"""
        error = Exception("Executor not found or route failed")
        category = error_handler.categorize_error(error)
        assert category == ErrorCategory.ROUTING
    
    def test_categorize_error_configuration(self, error_handler):
        """测试分类配置错误"""
        error = Exception("Configuration error in system config")
        category = error_handler.categorize_error(error)
        assert category == ErrorCategory.CONFIGURATION
    
    def test_categorize_error_execution(self, error_handler):
        """测试分类执行错误"""
        error = RuntimeError("Execution failed")
        category = error_handler.categorize_error(error)
        assert category == ErrorCategory.EXECUTION
    
    def test_categorize_error_unknown(self, error_handler):
        """测试分类未知错误"""
        error = Exception("Something unexpected happened")
        category = error_handler.categorize_error(error)
        assert category == ErrorCategory.UNKNOWN
    
    def test_format_error_message_network(self, error_handler):
        """测试格式化网络错误消息"""
        error = Exception("Connection timeout")
        message = error_handler.format_error_message(error)
        
        assert "网络连接失败" in message
        assert "Connection timeout" in message
        assert "检查网络连接" in message
    
    def test_format_error_message_auth(self, error_handler):
        """测试格式化认证错误消息"""
        error = Exception("Invalid API key")
        message = error_handler.format_error_message(error)
        
        assert "认证失败" in message
        assert "API Key" in message
    
    def test_format_error_message_rate_limit(self, error_handler):
        """测试格式化速率限制消息"""
        error = Exception("Rate limit exceeded")
        message = error_handler.format_error_message(error)
        
        assert "请求频率超限" in message
        assert "稍后重试" in message
    
    def test_format_error_message_without_details(self, error_handler):
        """测试格式化错误消息（不包含详细信息）"""
        error = Exception("Some error")
        message = error_handler.format_error_message(error, include_details=False)
        
        assert "Some error" not in message
    
    def test_format_error_message_without_suggestion(self, error_handler):
        """测试格式化错误消息（不包含建议）"""
        error = Exception("Network error")
        message = error_handler.format_error_message(error, include_suggestion=False)
        
        assert "建议" not in message
    
    def test_handle_error_with_sender(self, error_handler, mock_message_sender):
        """测试处理错误并发送消息"""
        error = Exception("Test error")
        
        result = error_handler.handle_error(
            error=error,
            chat_type="p2p",
            chat_id="chat_123",
            message_id="msg_456"
        )
        
        # 验证返回了错误消息
        assert "❌" in result
        assert "Test error" in result
        
        # 验证发送了消息
        mock_message_sender.send_message.assert_called_once()
        call_args = mock_message_sender.send_message.call_args[0]
        assert call_args[0] == "p2p"
        assert call_args[1] == "chat_123"
        assert call_args[2] == "msg_456"
    
    def test_handle_error_without_sender(self):
        """测试处理错误（无消息发送器）"""
        error_handler = ErrorHandler(message_sender=None)
        error = Exception("Test error")
        
        result = error_handler.handle_error(error)
        
        # 验证返回了错误消息
        assert "❌" in result
    
    def test_handle_error_sender_fails(self, error_handler, mock_message_sender):
        """测试消息发送失败时的处理"""
        mock_message_sender.send_message.side_effect = Exception("Send failed")
        
        error = Exception("Test error")
        
        # 不应该抛出异常
        result = error_handler.handle_error(
            error=error,
            chat_type="p2p",
            chat_id="chat_123",
            message_id="msg_456"
        )
        
        # 仍然返回错误消息
        assert "❌" in result


class TestErrorHandlerDecorators:
    """错误处理装饰器测试类"""
    
    def test_handle_errors_decorator(self):
        """测试错误处理装饰器"""
        from src.xagent.core.error_handler import handle_errors
        
        @handle_errors
        def failing_function():
            raise ValueError("Test error")
        
        # 应该抛出原始异常
        with pytest.raises(ValueError, match="Test error"):
            failing_function()
    
    def test_handle_errors_decorator_success(self):
        """测试错误处理装饰器（成功情况）"""
        from src.xagent.core.error_handler import handle_errors
        
        @handle_errors
        def success_function():
            return "success"
        
        result = success_function()
        assert result == "success"
    
    def test_safe_execute_success(self):
        """测试安全执行（成功）"""
        from src.xagent.core.error_handler import safe_execute
        
        def success_func():
            return "result"
        
        result = safe_execute(success_func)
        assert result == "result"
    
    def test_safe_execute_failure(self):
        """测试安全执行（失败）"""
        from src.xagent.core.error_handler import safe_execute
        
        def failing_func():
            raise ValueError("Test error")
        
        result = safe_execute(failing_func, default="default_value")
        assert result == "default_value"
    
    def test_safe_execute_with_args(self):
        """测试安全执行（带参数）"""
        from src.xagent.core.error_handler import safe_execute
        
        def func_with_args(a, b):
            return a + b
        
        result = safe_execute(func_with_args, 0, 1, 2)
        assert result == 3
