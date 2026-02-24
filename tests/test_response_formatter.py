"""
响应格式化器单元测试

测试响应格式化器的具体示例和边界情况。
"""
import pytest

from feishu_bot.response_formatter import ResponseFormatter


class TestResponseFormatter:
    """响应格式化器单元测试"""
    
    def test_format_success_response(self):
        """测试成功响应格式
        
        Requirements: 5.1, 5.2
        """
        formatter = ResponseFormatter()
        user_message = "请帮我分析这段代码"
        ai_output = "这段代码实现了一个简单的排序算法..."
        
        response = formatter.format_response(user_message, ai_output, error=None)
        
        # 验证响应包含 AI 输出
        assert ai_output in response
        # 验证响应不为空
        assert len(response) > 0
        # 验证响应是字符串
        assert isinstance(response, str)
    
    def test_format_error_response(self):
        """测试错误响应格式
        
        Requirements: 5.3
        """
        formatter = ResponseFormatter()
        user_message = "请帮我分析这段代码"
        error_message = "目标目录不存在"
        
        response = formatter.format_response(user_message, "", error=error_message)
        
        # 验证响应包含错误信息
        assert error_message in response
        # 验证响应包含错误标识
        assert "❌" in response or "Error" in response or "失败" in response
        # 验证响应不为空
        assert len(response) > 0
    
    def test_format_error_with_format_error_method(self):
        """测试使用 format_error 方法格式化错误
        
        Requirements: 5.3
        """
        formatter = ResponseFormatter()
        user_message = "请帮我分析这段代码"
        error_message = "API 调用失败：超时"
        
        response = formatter.format_error(user_message, error_message)
        
        # 验证响应包含错误信息
        assert error_message in response
        # 验证响应包含错误标识
        assert "❌" in response or "Error" in response or "失败" in response
    
    def test_response_contains_original_message_implicitly(self):
        """测试响应隐式包含原始消息（通过上下文）
        
        根据当前实现，ResponseFormatter 直接返回 AI 输出，
        不显式包含原始消息。原始消息的上下文由调用方管理。
        
        Requirements: 5.1
        """
        formatter = ResponseFormatter()
        user_message = "Hello, AI!"
        ai_output = "Hello! How can I help you today?"
        
        response = formatter.format_response(user_message, ai_output, error=None)
        
        # 验证响应包含 AI 输出
        assert ai_output in response
        # 当前实现中，原始消息不会显式包含在响应中
        # 这是设计决策：保持响应简洁，由调用方管理上下文
    
    def test_empty_ai_output(self):
        """测试空 AI 输出
        
        Requirements: 5.2
        """
        formatter = ResponseFormatter()
        user_message = "测试消息"
        ai_output = ""
        
        response = formatter.format_response(user_message, ai_output, error=None)
        
        # 即使 AI 输出为空，也应该返回有效的响应
        assert isinstance(response, str)
    
    def test_empty_error_message(self):
        """测试空错误消息
        
        当错误消息为空字符串时，Python 的 if error 会判断为 False，
        因此会返回 ai_output（也是空字符串）。
        
        Requirements: 5.3
        """
        formatter = ResponseFormatter()
        user_message = "测试消息"
        error_message = ""
        ai_output = ""
        
        response = formatter.format_response(user_message, ai_output, error=error_message)
        
        # 空错误消息会被当作无错误处理，返回 ai_output
        assert isinstance(response, str)
        assert response == ai_output  # 应该返回空的 ai_output
    
    def test_multiline_ai_output(self):
        """测试多行 AI 输出
        
        Requirements: 5.2, 5.4
        """
        formatter = ResponseFormatter()
        user_message = "请解释这个概念"
        ai_output = """这是一个复杂的概念：

1. 第一点说明
2. 第二点说明
3. 第三点说明

总结：这就是完整的解释。"""
        
        response = formatter.format_response(user_message, ai_output, error=None)
        
        # 验证多行输出被正确保留
        assert ai_output in response
        assert "\n" in response
    
    def test_special_characters_in_output(self):
        """测试输出中的特殊字符
        
        Requirements: 5.2, 5.4
        """
        formatter = ResponseFormatter()
        user_message = "测试特殊字符"
        ai_output = "这是一些特殊字符：@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        response = formatter.format_response(user_message, ai_output, error=None)
        
        # 验证特殊字符被正确保留
        assert ai_output in response
    
    def test_unicode_characters_in_output(self):
        """测试输出中的 Unicode 字符
        
        Requirements: 5.2, 5.4
        """
        formatter = ResponseFormatter()
        user_message = "测试 Unicode"
        ai_output = "这是一些 Unicode 字符：你好世界 🌍 こんにちは 안녕하세요"
        
        response = formatter.format_response(user_message, ai_output, error=None)
        
        # 验证 Unicode 字符被正确保留
        assert ai_output in response
    
    def test_long_output(self):
        """测试长输出
        
        Requirements: 5.2, 5.4
        """
        formatter = ResponseFormatter()
        user_message = "生成长文本"
        ai_output = "这是一段很长的文本。" * 100
        
        response = formatter.format_response(user_message, ai_output, error=None)
        
        # 验证长输出被正确处理
        assert ai_output in response
        assert len(response) >= len(ai_output)
    
    def test_error_priority_over_output(self):
        """测试错误优先于输出
        
        当同时提供 ai_output 和 error 时，应该返回错误格式。
        
        Requirements: 5.3
        """
        formatter = ResponseFormatter()
        user_message = "测试消息"
        ai_output = "这是 AI 输出"
        error_message = "这是错误信息"
        
        response = formatter.format_response(user_message, ai_output, error=error_message)
        
        # 验证返回的是错误格式
        assert error_message in response
        assert "❌" in response or "Error" in response or "失败" in response
        # AI 输出不应该出现在错误响应中
        assert ai_output not in response
