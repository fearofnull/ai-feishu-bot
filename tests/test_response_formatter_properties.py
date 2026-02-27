"""
响应格式化器属性测试

测试响应格式化器的通用正确性属性。
"""
import pytest
from hypothesis import given, strategies as st

from feishu_bot.response_formatter import ResponseFormatter


# Feature: feishu-ai-bot, Property 11: 响应消息完整性
# Validates: Requirements 5.1, 5.2, 5.4
@given(
    user_message=st.text(min_size=1, max_size=500),
    ai_output=st.text(min_size=1, max_size=1000)
)
def test_response_message_integrity(user_message: str, ai_output: str):
    """
    Property 11: 响应消息完整性
    
    For any 用户消息和 AI 输出，格式化的响应应该：
    - 包含 AI 的输出
    - 使用清晰的分隔符（如 "\n\n" 或标题行）分隔不同部分
    
    Validates: Requirements 5.1, 5.2, 5.4
    """
    formatter = ResponseFormatter()
    
    # 格式化成功响应
    response = formatter.format_response(user_message, ai_output, error=None)
    
    # 验证响应包含 AI 输出
    assert ai_output in response, "Response should contain AI output"
    
    # 验证响应不为空
    assert len(response) > 0, "Response should not be empty"
    
    # 验证响应是字符串类型
    assert isinstance(response, str), "Response should be a string"


@given(
    user_message=st.text(min_size=1, max_size=500),
    error_message=st.text(min_size=1, max_size=500)
)
def test_error_response_integrity(user_message: str, error_message: str):
    """
    Property 11 (Error case): 错误响应完整性
    
    For any 用户消息和错误信息，格式化的错误响应应该：
    - 包含错误信息
    - 使用清晰的错误标识（如 "❌" 或 "Error"）
    
    Validates: Requirements 5.3, 5.4
    """
    formatter = ResponseFormatter()
    
    # 格式化错误响应
    response = formatter.format_response(user_message, "", error=error_message)
    
    # 验证响应包含错误信息
    assert error_message in response, "Error response should contain error message"
    
    # 验证响应包含错误标识
    assert "❌" in response or "Error" in response or "错误" in response or "失败" in response, \
        "Error response should contain error indicator"
    
    # 验证响应不为空
    assert len(response) > 0, "Error response should not be empty"
    
    # 验证响应是字符串类型
    assert isinstance(response, str), "Error response should be a string"


@given(
    user_message=st.text(min_size=1, max_size=500),
    ai_output=st.text(min_size=1, max_size=1000)
)
def test_response_format_consistency(user_message: str, ai_output: str):
    """
    Property 11 (Consistency): 响应格式一致性
    
    For any 相同的输入，格式化器应该产生相同的输出（幂等性）。
    
    Validates: Requirements 5.4
    """
    formatter = ResponseFormatter()
    
    # 多次格式化相同的输入
    response1 = formatter.format_response(user_message, ai_output, error=None)
    response2 = formatter.format_response(user_message, ai_output, error=None)
    
    # 验证输出一致
    assert response1 == response2, "Formatter should produce consistent output for same input"


@given(
    user_message=st.text(min_size=1, max_size=500),
    error_message=st.text(min_size=1, max_size=500)
)
def test_error_format_consistency(user_message: str, error_message: str):
    """
    Property 11 (Error Consistency): 错误格式一致性
    
    For any 相同的错误输入，格式化器应该产生相同的错误输出（幂等性）。
    
    Validates: Requirements 5.3, 5.4
    """
    formatter = ResponseFormatter()
    
    # 多次格式化相同的错误输入
    response1 = formatter.format_response(user_message, "", error=error_message)
    response2 = formatter.format_response(user_message, "", error=error_message)
    
    # 验证输出一致
    assert response1 == response2, "Formatter should produce consistent error output for same input"
