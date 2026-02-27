"""
单元测试：消息发送器

测试 MessageSender 的错误处理和边界情况。
Requirements: 6.3
"""
import pytest
from unittest.mock import Mock, MagicMock
from feishu_bot.message_sender import MessageSender


class TestMessageSenderErrorHandling:
    """测试消息发送器的错误处理"""
    
    def test_api_call_failure_returns_false(self):
        """
        测试 API 调用失败时返回 False
        
        Validates: Requirements 6.3
        """
        # 创建 mock 客户端，模拟 API 调用失败
        mock_client = Mock()
        mock_response = Mock()
        mock_response.success.return_value = False
        mock_response.code = 1001
        mock_response.msg = "API call failed"
        mock_response.get_log_id.return_value = "log_12345"
        mock_client.im.v1.message.create.return_value = mock_response
        
        sender = MessageSender(mock_client)
        
        # 发送消息
        result = sender.send_message(
            chat_type="p2p",
            chat_id="test_chat_id",
            message_id="test_message_id",
            content="test content"
        )
        
        # 验证返回 False
        assert result is False, "API 调用失败应该返回 False"
    
    def test_api_failure_logs_error_details(self, caplog):
        """
        测试 API 调用失败时记录错误详情
        
        验证错误日志包含 code, msg, log_id
        
        Validates: Requirements 6.3
        """
        # 创建 mock 客户端
        mock_client = Mock()
        mock_response = Mock()
        mock_response.success.return_value = False
        mock_response.code = 1001
        mock_response.msg = "Invalid parameter"
        mock_response.get_log_id.return_value = "log_abc123"
        mock_client.im.v1.message.create.return_value = mock_response
        
        sender = MessageSender(mock_client)
        
        # 发送消息
        with caplog.at_level("ERROR"):
            sender.send_new_message("test_chat_id", "test content")
        
        # 验证日志包含错误详情
        log_text = caplog.text
        assert "code=1001" in log_text, "日志应该包含错误代码"
        assert "msg=Invalid parameter" in log_text, "日志应该包含错误消息"
        assert "log_id=log_abc123" in log_text, "日志应该包含日志 ID"
    
    def test_reply_message_api_failure_logs_details(self, caplog):
        """
        测试回复消息 API 调用失败时记录错误详情
        
        Validates: Requirements 6.3
        """
        # 创建 mock 客户端
        mock_client = Mock()
        mock_response = Mock()
        mock_response.success.return_value = False
        mock_response.code = 2001
        mock_response.msg = "Message not found"
        mock_response.get_log_id.return_value = "log_xyz789"
        mock_client.im.v1.message.reply.return_value = mock_response
        
        sender = MessageSender(mock_client)
        
        # 回复消息
        with caplog.at_level("ERROR"):
            sender.reply_message("test_message_id", "test content")
        
        # 验证日志包含错误详情
        log_text = caplog.text
        assert "code=2001" in log_text, "日志应该包含错误代码"
        assert "msg=Message not found" in log_text, "日志应该包含错误消息"
        assert "log_id=log_xyz789" in log_text, "日志应该包含日志 ID"
    
    def test_exception_during_send_returns_false(self):
        """
        测试发送过程中抛出异常时返回 False
        
        Validates: Requirements 6.3
        """
        # 创建 mock 客户端，模拟抛出异常
        mock_client = Mock()
        mock_client.im.v1.message.create.side_effect = Exception("Network error")
        
        sender = MessageSender(mock_client)
        
        # 发送消息
        result = sender.send_message(
            chat_type="p2p",
            chat_id="test_chat_id",
            message_id="test_message_id",
            content="test content"
        )
        
        # 验证返回 False
        assert result is False, "异常情况应该返回 False"
    
    def test_exception_during_reply_returns_false(self):
        """
        测试回复过程中抛出异常时返回 False
        
        Validates: Requirements 6.3
        """
        # 创建 mock 客户端，模拟抛出异常
        mock_client = Mock()
        mock_client.im.v1.message.reply.side_effect = Exception("Connection timeout")
        
        sender = MessageSender(mock_client)
        
        # 发送消息
        result = sender.send_message(
            chat_type="group",
            chat_id="test_chat_id",
            message_id="test_message_id",
            content="test content"
        )
        
        # 验证返回 False
        assert result is False, "异常情况应该返回 False"


class TestMessageSenderJSONEscaping:
    """测试消息内容的 JSON 转义"""
    
    def test_escape_special_characters(self):
        """
        测试特殊字符的转义
        
        验证消息内容中的特殊字符被正确转义
        """
        mock_client = Mock()
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_client.im.v1.message.create.return_value = mock_response
        
        sender = MessageSender(mock_client)
        
        # 发送包含特殊字符的消息
        content = 'Test "quotes" and \n newlines \t tabs \\ backslash'
        sender.send_new_message("test_chat_id", content)
        
        # 获取实际发送的内容
        call_args = mock_client.im.v1.message.create.call_args
        request = call_args[0][0]
        sent_content = request.body.content
        
        # 验证特殊字符被转义
        assert '\\"' in sent_content, "双引号应该被转义"
        assert '\\n' in sent_content, "换行符应该被转义"
        assert '\\t' in sent_content, "制表符应该被转义"
        assert '\\\\' in sent_content, "反斜杠应该被转义"
    
    def test_escape_carriage_return(self):
        """
        测试回车符的转义
        """
        mock_client = Mock()
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_client.im.v1.message.create.return_value = mock_response
        
        sender = MessageSender(mock_client)
        
        # 发送包含回车符的消息
        content = 'Line 1\rLine 2'
        sender.send_new_message("test_chat_id", content)
        
        # 获取实际发送的内容
        call_args = mock_client.im.v1.message.create.call_args
        request = call_args[0][0]
        sent_content = request.body.content
        
        # 验证回车符被转义
        assert '\\r' in sent_content, "回车符应该被转义"


class TestMessageSenderSuccessLogging:
    """测试成功发送时的日志记录"""
    
    def test_successful_send_logs_info(self, caplog):
        """
        测试成功发送消息时记录 INFO 日志
        """
        mock_client = Mock()
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_client.im.v1.message.create.return_value = mock_response
        
        sender = MessageSender(mock_client)
        
        # 发送消息
        with caplog.at_level("INFO"):
            sender.send_new_message("test_chat_id", "test content")
        
        # 验证日志
        assert "Successfully sent new message" in caplog.text
        assert "test_chat_id" in caplog.text
    
    def test_successful_reply_logs_info(self, caplog):
        """
        测试成功回复消息时记录 INFO 日志
        """
        mock_client = Mock()
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_client.im.v1.message.reply.return_value = mock_response
        
        sender = MessageSender(mock_client)
        
        # 回复消息
        with caplog.at_level("INFO"):
            sender.reply_message("test_message_id", "test content")
        
        # 验证日志
        assert "Successfully replied to message" in caplog.text
        assert "test_message_id" in caplog.text
