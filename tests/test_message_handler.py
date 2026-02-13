"""
MessageHandler 单元测试
"""
import json
import pytest
from unittest.mock import Mock, MagicMock
from feishu_bot.message_handler import MessageHandler
from feishu_bot.cache import DeduplicationCache


class TestMessageHandler:
    """MessageHandler 单元测试类"""
    
    @pytest.fixture
    def mock_client(self):
        """创建模拟的飞书客户端"""
        return Mock()
    
    @pytest.fixture
    def dedup_cache(self):
        """创建消息去重缓存"""
        return DeduplicationCache(max_size=100)
    
    @pytest.fixture
    def handler(self, mock_client, dedup_cache):
        """创建 MessageHandler 实例"""
        return MessageHandler(mock_client, dedup_cache)
    
    def test_parse_text_message_success(self, handler):
        """测试成功解析文本消息"""
        message = {
            "message_type": "text",
            "content": json.dumps({"text": "Hello, World!"})
        }
        
        result = handler.parse_message_content(message)
        assert result == "Hello, World!"
    
    def test_parse_non_text_message_raises_error(self, handler):
        """测试非文本消息抛出错误"""
        message = {
            "message_type": "image",
            "content": json.dumps({"image_key": "img_xxx"})
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        assert "不支持的消息类型" in str(exc_info.value)
        assert "请发送文本消息" in str(exc_info.value)
    
    def test_parse_message_with_empty_content(self, handler):
        """测试空内容消息"""
        message = {
            "message_type": "text",
            "content": json.dumps({"text": ""})
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        assert "消息内容为空" in str(exc_info.value)
    
    def test_parse_message_with_invalid_json(self, handler):
        """测试无效 JSON 内容"""
        message = {
            "message_type": "text",
            "content": "invalid json"
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        assert "JSON 解析失败" in str(exc_info.value)
    
    def test_combine_messages_with_quoted(self, handler):
        """测试组合引用消息和当前消息"""
        quoted = "这是引用的消息"
        current = "这是当前消息"
        
        result = handler.combine_messages(quoted, current)
        
        assert "引用消息：这是引用的消息" in result
        assert "当前消息：这是当前消息" in result
        assert result.count("\n\n") == 1  # 确保有分隔符
    
    def test_combine_messages_without_quoted(self, handler):
        """测试没有引用消息时只返回当前消息"""
        current = "这是当前消息"
        
        result = handler.combine_messages(None, current)
        
        assert result == current
        assert "引用消息" not in result
    
    def test_get_quoted_message_with_empty_parent_id(self, handler):
        """测试空的 parent_id 返回 None"""
        result = handler.get_quoted_message("")
        assert result is None
        
        result = handler.get_quoted_message(None)
        assert result is None
    
    def test_get_quoted_message_text_success(self, handler, mock_client):
        """测试成功获取引用的文本消息"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_response.data.message.message_type = "text"
        mock_response.data.message.content = json.dumps({"text": "引用的文本"})
        
        mock_client.im.v1.message.get.return_value = mock_response
        
        result = handler.get_quoted_message("msg_123")
        
        assert result == "引用的文本"
        mock_client.im.v1.message.get.assert_called_once()
    
    def test_get_quoted_message_interactive_with_title(self, handler, mock_client):
        """测试获取引用的卡片消息（有标题）"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_response.data.message.message_type = "interactive"
        mock_response.data.message.content = json.dumps({
            "header": {
                "title": {
                    "content": "卡片标题"
                }
            }
        })
        
        mock_client.im.v1.message.get.return_value = mock_response
        
        result = handler.get_quoted_message("msg_123")
        
        assert result == "[卡片消息] 卡片标题"
    
    def test_get_quoted_message_interactive_without_title(self, handler, mock_client):
        """测试获取引用的卡片消息（无标题）"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_response.data.message.message_type = "interactive"
        mock_response.data.message.content = json.dumps({})
        
        mock_client.im.v1.message.get.return_value = mock_response
        
        result = handler.get_quoted_message("msg_123")
        
        assert result == "[卡片消息]"
    
    def test_get_quoted_message_api_failure(self, handler, mock_client):
        """测试 API 调用失败返回 None"""
        # 模拟 API 失败响应
        mock_response = Mock()
        mock_response.success.return_value = False
        mock_response.code = 400
        mock_response.msg = "Bad Request"
        mock_response.get_log_id.return_value = "log_123"
        
        mock_client.im.v1.message.get.return_value = mock_response
        
        result = handler.get_quoted_message("msg_123")
        
        assert result is None
    
    def test_get_quoted_message_unsupported_type(self, handler, mock_client):
        """测试不支持的消息类型"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_response.data.message.message_type = "file"
        mock_response.data.message.content = json.dumps({})
        
        mock_client.im.v1.message.get.return_value = mock_response
        
        result = handler.get_quoted_message("msg_123")
        
        assert result == "[file 消息]"
    
    def test_get_quoted_message_exception(self, handler, mock_client):
        """测试获取引用消息时发生异常"""
        # 模拟异常
        mock_client.im.v1.message.get.side_effect = Exception("Network error")
        
        result = handler.get_quoted_message("msg_123")
        
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
