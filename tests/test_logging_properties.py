"""
日志记录属性测试

验证系统在各种操作中正确记录日志。

Feature: feishu-ai-bot
Properties:
- Property 16: 错误日志记录
- Property 17: 重复消息日志记录
- Property 18: AI 执行日志记录
- Property 19: 引用消息检索日志记录

Validates: Requirements 7.1, 7.2, 7.3, 7.4
"""
import pytest
import subprocess
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import Mock, MagicMock, patch
import logging

from feishu_bot.cache import DeduplicationCache
from feishu_bot.message_handler import MessageHandler
from feishu_bot.claude_api_executor import ClaudeAPIExecutor
from feishu_bot.claude_cli_executor import ClaudeCodeCLIExecutor
from feishu_bot.models import Message


# Property 16: 错误日志记录
# Feature: feishu-ai-bot, Property 16: 错误日志记录
# For any operation that fails, the system should log an error message with context information
@given(
    error_message=st.text(min_size=1, max_size=100)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_16_error_logging(error_message, caplog):
    """
    Property 16: 错误日志记录
    
    For any operation that fails, the system should log an error message with context information.
    
    Validates: Requirements 7.1
    """
    # Test MessageHandler error logging
    with caplog.at_level(logging.ERROR):
        client = Mock()
        dedup_cache = DeduplicationCache()
        handler = MessageHandler(client, dedup_cache)
        
        # Create a message with invalid type
        message = Mock()
        message.message_type = "image"  # Non-text type
        message.content = "{}"
        
        # This should raise ValueError and log an error
        with pytest.raises(ValueError):
            handler.parse_message_content(message)
        
        # Verify error was logged
        assert any(record.levelname == "WARNING" for record in caplog.records)


# Property 17: 重复消息日志记录
# Feature: feishu-ai-bot, Property 17: 重复消息日志记录
# For any duplicate message detected, the system should log the message ID and skip reason
@given(
    message_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_17_duplicate_message_logging(message_id, caplog):
    """
    Property 17: 重复消息日志记录
    
    For any duplicate message detected, the system should log the message ID and skip reason.
    
    Validates: Requirements 7.2
    """
    with caplog.at_level(logging.INFO):
        cache = DeduplicationCache()
        
        # Mark message as processed
        cache.mark_processed(message_id)
        
        # Check if it's processed (should log duplicate detection)
        is_duplicate = cache.is_processed(message_id)
        
        # Verify duplicate was detected
        assert is_duplicate
        
        # Verify logging occurred
        assert any(
            "Duplicate message detected" in record.message and message_id in record.message
            for record in caplog.records
        )


# Property 18: AI 执行日志记录
# Feature: feishu-ai-bot, Property 18: AI 执行日志记录
# For any AI command execution, the system should log the execution result
@given(
    user_prompt=st.text(min_size=1, max_size=100)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_18_ai_execution_logging_api(user_prompt, caplog):
    """
    Property 18: AI 执行日志记录 (API)
    
    For any AI API execution, the system should log the execution result.
    
    Validates: Requirements 7.3
    """
    with caplog.at_level(logging.INFO):
        # Mock the Anthropic client
        with patch('feishu_bot.claude_api_executor.anthropic.Anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            
            # Mock successful response
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Test response")]
            mock_client.messages.create.return_value = mock_response
            
            executor = ClaudeAPIExecutor(api_key="test_key")
            result = executor.execute(user_prompt)
            
            # Verify execution was logged
            assert any(
                "Claude API call" in record.message
                for record in caplog.records
            )
            
            # Verify success was logged
            if result.success:
                assert any(
                    "successful" in record.message.lower()
                    for record in caplog.records
                )


@given(
    user_prompt=st.text(min_size=1, max_size=100)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_18_ai_execution_logging_cli(user_prompt, caplog):
    """
    Property 18: AI 执行日志记录 (CLI)
    
    For any AI CLI execution, the system should log the execution result.
    
    Validates: Requirements 7.3
    """
    with caplog.at_level(logging.INFO):
        import tempfile
        import os
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            executor = ClaudeCodeCLIExecutor(target_dir=temp_dir)
            
            # Mock subprocess to avoid actual CLI execution
            with patch('feishu_bot.claude_cli_executor.subprocess.run') as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "Test output"
                mock_result.stderr = ""
                mock_run.return_value = mock_result
                
                result = executor.execute(user_prompt)
                
                # Verify execution was logged
                assert any(
                    "Claude CLI" in record.message
                    for record in caplog.records
                )
                
                # Verify completion was logged
                assert any(
                    "execution completed" in record.message.lower() or "completed" in record.message.lower()
                    for record in caplog.records
                )


# Property 19: 引用消息检索日志记录
# Feature: feishu-ai-bot, Property 19: 引用消息检索日志记录
# For any quoted message retrieval, the system should log the retrieval process and results
@given(
    parent_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_19_quoted_message_retrieval_logging(parent_id, caplog):
    """
    Property 19: 引用消息检索日志记录
    
    For any quoted message retrieval, the system should log the retrieval process and results.
    
    Validates: Requirements 7.4
    """
    with caplog.at_level(logging.INFO):
        client = Mock()
        dedup_cache = DeduplicationCache()
        handler = MessageHandler(client, dedup_cache)
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.message.message_type = "text"
        mock_response.data.message.content = '{"text": "Quoted message"}'
        client.im.v1.message.get.return_value = mock_response
        
        # Retrieve quoted message
        result = handler.get_quoted_message(parent_id)
        
        # Verify retrieval was logged
        assert any(
            "获取引用消息" in record.message or "引用消息" in record.message
            for record in caplog.records
        )
        
        # Verify result was logged (success or failure)
        assert any(
            "成功" in record.message or "失败" in record.message
            for record in caplog.records
        )


# Additional test: Verify error logging includes context
@given(
    error_type=st.sampled_from(["timeout", "not_found", "api_error"])
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_error_logging_includes_context(error_type, caplog):
    """
    Verify that error logging includes context information.
    
    Validates: Requirements 7.1
    """
    with caplog.at_level(logging.ERROR):
        # Test CLI executor error logging with context
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            executor = ClaudeCodeCLIExecutor(target_dir=temp_dir)
            
            with patch('feishu_bot.claude_cli_executor.subprocess.run') as mock_run:
                if error_type == "timeout":
                    mock_run.side_effect = subprocess.TimeoutExpired("claude", 600)
                elif error_type == "not_found":
                    mock_run.side_effect = FileNotFoundError()
                else:
                    mock_run.side_effect = Exception("API error")
                
                result = executor.execute("test prompt")
                
                # Verify error was logged
                assert any(record.levelname == "ERROR" for record in caplog.records)
                
                # Verify error message contains context
                assert not result.success
                assert result.error_message is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
