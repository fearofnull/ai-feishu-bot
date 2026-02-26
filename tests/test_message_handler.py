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
        
        assert result == "[卡片消息]\n卡片标题"
    
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


class TestCardMessageProcessing:
    """卡片消息处理单元测试类 - 验证需求 1.1, 1.3, 2.3"""
    
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
    
    def test_parse_card_message_with_header_and_elements(self, handler):
        """测试包含 header 和 elements 的完整卡片消息"""
        card_content = {
            "header": {
                "title": {
                    "content": "任务提醒"
                }
            },
            "elements": [
                {
                    "tag": "text",
                    "content": "您有一个新任务需要处理"
                },
                {
                    "tag": "markdown",
                    "content": "**截止日期**: 2024-01-15"
                }
            ]
        }
        
        message = {
            "message_type": "interactive",
            "content": json.dumps(card_content)
        }
        
        result = handler.parse_message_content(message)
        
        # 验证返回内容格式正确
        assert result.startswith("[卡片消息]")
        # 验证包含所有文本内容
        assert "任务提醒" in result
        assert "您有一个新任务需要处理" in result
        assert "**截止日期**: 2024-01-15" in result
    
    def test_parse_card_message_elements_only(self, handler):
        """测试仅包含 elements 的卡片消息（无 header）"""
        card_content = {
            "elements": [
                {
                    "tag": "text",
                    "content": "这是一条简单的卡片消息"
                },
                {
                    "tag": "div",
                    "text": {
                        "content": "包含在 div 中的文本"
                    }
                }
            ]
        }
        
        message = {
            "message_type": "interactive",
            "content": json.dumps(card_content)
        }
        
        result = handler.parse_message_content(message)
        
        # 验证返回内容格式正确
        assert result.startswith("[卡片消息]")
        # 验证包含所有文本内容
        assert "这是一条简单的卡片消息" in result
        assert "包含在 div 中的文本" in result
    
    def test_parse_card_message_with_multiple_element_types(self, handler):
        """测试包含多种元素类型的卡片（text、markdown、button、div）"""
        card_content = {
            "header": {
                "title": {
                    "content": "多元素卡片"
                }
            },
            "elements": [
                {
                    "tag": "text",
                    "content": "普通文本元素"
                },
                {
                    "tag": "markdown",
                    "content": "**加粗文本** 和 *斜体文本*"
                },
                {
                    "tag": "div",
                    "text": {
                        "content": "Div 容器中的文本"
                    }
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "content": "确认按钮"
                            }
                        },
                        {
                            "tag": "button",
                            "text": {
                                "content": "取消按钮"
                            }
                        }
                    ]
                }
            ]
        }
        
        message = {
            "message_type": "interactive",
            "content": json.dumps(card_content)
        }
        
        result = handler.parse_message_content(message)
        
        # 验证返回内容格式正确
        assert result.startswith("[卡片消息]")
        # 验证包含所有元素的文本
        assert "多元素卡片" in result
        assert "普通文本元素" in result
        assert "**加粗文本** 和 *斜体文本*" in result
        assert "Div 容器中的文本" in result
        assert "确认按钮" in result
        assert "取消按钮" in result
    
    def test_parse_card_message_event_message_format(self, handler):
        """测试 EventMessage 对象格式的卡片消息"""
        card_content = {
            "header": {
                "title": {
                    "content": "EventMessage 格式测试"
                }
            },
            "elements": [
                {
                    "tag": "text",
                    "content": "使用 EventMessage 对象格式"
                }
            ]
        }
        
        # 创建模拟的 EventMessage 对象
        event_message = Mock()
        event_message.message_type = "interactive"
        event_message.content = json.dumps(card_content)
        
        result = handler.parse_message_content(event_message)
        
        # 验证返回内容格式正确
        assert result.startswith("[卡片消息]")
        assert "EventMessage 格式测试" in result
        assert "使用 EventMessage 对象格式" in result
    
    def test_parse_card_message_dict_format(self, handler):
        """测试字典格式的卡片消息"""
        card_content = {
            "header": {
                "title": {
                    "content": "字典格式测试"
                }
            },
            "elements": [
                {
                    "tag": "text",
                    "content": "使用字典格式"
                }
            ]
        }
        
        message = {
            "message_type": "interactive",
            "content": json.dumps(card_content)
        }
        
        result = handler.parse_message_content(message)
        
        # 验证返回内容格式正确
        assert result.startswith("[卡片消息]")
        assert "字典格式测试" in result
        assert "使用字典格式" in result
    
    def test_parse_card_message_both_formats_produce_same_result(self, handler):
        """测试 EventMessage 对象格式和字典格式产生相同的结果"""
        card_content = {
            "header": {
                "title": {
                    "content": "格式兼容性测试"
                }
            },
            "elements": [
                {
                    "tag": "text",
                    "content": "测试两种格式的兼容性"
                }
            ]
        }
        
        # EventMessage 对象格式
        event_message = Mock()
        event_message.message_type = "interactive"
        event_message.content = json.dumps(card_content)
        
        # 字典格式
        dict_message = {
            "message_type": "interactive",
            "content": json.dumps(card_content)
        }
        
        result_event = handler.parse_message_content(event_message)
        result_dict = handler.parse_message_content(dict_message)
        
        # 验证两种格式产生相同的结果
        assert result_event == result_dict


class TestCardMessageErrorHandling:
    """卡片消息错误处理单元测试类 - 验证需求 2.4, 2.5, 3.4, 4.1, 4.2"""
    
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
    
    def test_parse_card_message_with_invalid_json(self, handler):
        """测试无效 JSON 的卡片消息，验证抛出 ValueError 且错误消息清晰"""
        message = {
            "message_type": "interactive",
            "content": "invalid json content {not valid}"
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        # 验证错误消息清晰且包含关键信息
        error_message = str(exc_info.value)
        assert "卡片消息内容 JSON 解析失败" in error_message
    
    def test_parse_card_message_with_empty_content(self, handler):
        """测试空内容的卡片消息，验证抛出 ValueError 且错误消息清晰"""
        # 测试完全空的卡片
        message = {
            "message_type": "interactive",
            "content": json.dumps({})
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        # 验证错误消息清晰
        error_message = str(exc_info.value)
        assert "卡片消息内容为空" in error_message
    
    def test_parse_card_message_with_only_empty_elements(self, handler):
        """测试只包含空元素的卡片消息"""
        card_content = {
            "elements": [
                {
                    "tag": "text",
                    "content": ""
                },
                {
                    "tag": "markdown",
                    "content": ""
                }
            ]
        }
        
        message = {
            "message_type": "interactive",
            "content": json.dumps(card_content)
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        # 验证错误消息清晰
        error_message = str(exc_info.value)
        assert "卡片消息内容为空" in error_message
    
    def test_parse_unsupported_message_type_image(self, handler):
        """测试不支持的消息类型 - image"""
        message = {
            "message_type": "image",
            "content": json.dumps({"image_key": "img_xxx"})
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        # 验证错误消息包含消息类型和提示信息
        error_message = str(exc_info.value)
        assert "不支持的消息类型" in error_message
        assert "image" in error_message
        assert "请发送文本消息或卡片消息" in error_message
    
    def test_parse_unsupported_message_type_file(self, handler):
        """测试不支持的消息类型 - file"""
        message = {
            "message_type": "file",
            "content": json.dumps({"file_key": "file_xxx"})
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        # 验证错误消息包含消息类型和提示信息
        error_message = str(exc_info.value)
        assert "不支持的消息类型" in error_message
        assert "file" in error_message
        assert "请发送文本消息或卡片消息" in error_message
    
    def test_parse_unsupported_message_type_audio(self, handler):
        """测试不支持的消息类型 - audio"""
        message = {
            "message_type": "audio",
            "content": json.dumps({"audio_key": "audio_xxx"})
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        # 验证错误消息包含消息类型和提示信息
        error_message = str(exc_info.value)
        assert "不支持的消息类型" in error_message
        assert "audio" in error_message
        assert "请发送文本消息或卡片消息" in error_message
    
    def test_parse_unsupported_message_type_video(self, handler):
        """测试不支持的消息类型 - video"""
        message = {
            "message_type": "video",
            "content": json.dumps({"video_key": "video_xxx"})
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        # 验证错误消息包含消息类型和提示信息
        error_message = str(exc_info.value)
        assert "不支持的消息类型" in error_message
        assert "video" in error_message
        assert "请发送文本消息或卡片消息" in error_message
    
    def test_parse_unsupported_message_type_unknown(self, handler):
        """测试未知的消息类型"""
        message = {
            "message_type": "unknown_type",
            "content": json.dumps({})
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        # 验证错误消息包含消息类型和提示信息
        error_message = str(exc_info.value)
        assert "不支持的消息类型" in error_message
        assert "unknown_type" in error_message
        assert "请发送文本消息或卡片消息" in error_message


class TestTextMessageBackwardCompatibility:
    """文本消息向后兼容性单元测试类 - 验证需求 1.2, 3.1, 3.2, 3.3"""
    
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
    
    def test_parse_plain_text_message_continues_to_work(self, handler):
        """测试普通文本消息继续正常工作"""
        message = {
            "message_type": "text",
            "content": json.dumps({"text": "这是一条普通的文本消息"})
        }
        
        result = handler.parse_message_content(message)
        
        # 验证返回值与原始实现一致
        assert result == "这是一条普通的文本消息"
        assert isinstance(result, str)
    
    def test_parse_text_message_with_mentions(self, handler):
        """测试包含@提及的文本消息"""
        # 测试包含 <at> 标签的消息
        message_with_at_tag = {
            "message_type": "text",
            "content": json.dumps({"text": '<at user_id="ou_123">张三</at> 你好，请查看这个问题'})
        }
        
        result = handler.parse_message_content(message_with_at_tag)
        
        # 验证@提及被正确清理
        assert "<at" not in result
        assert "ou_123" not in result
        assert "你好，请查看这个问题" in result
        
        # 测试包含 @_user_1 占位符的消息
        message_with_placeholder = {
            "message_type": "text",
            "content": json.dumps({"text": "@_user_1 @_user_2 大家好"})
        }
        
        result = handler.parse_message_content(message_with_placeholder)
        
        # 验证占位符被正确清理
        assert "@_user_1" not in result
        assert "@_user_2" not in result
        assert "大家好" in result
        
        # 测试包含 @_all 的消息
        message_with_all = {
            "message_type": "text",
            "content": json.dumps({"text": "@_all 重要通知：系统将在今晚维护"})
        }
        
        result = handler.parse_message_content(message_with_all)
        
        # 验证 @_all 被正确清理
        assert "@_all" not in result
        assert "重要通知：系统将在今晚维护" in result
    
    def test_parse_text_message_with_multiple_mentions(self, handler):
        """测试包含多个@提及的文本消息"""
        message = {
            "message_type": "text",
            "content": json.dumps({
                "text": '<at user_id="ou_123">张三</at> <at user_id="ou_456">李四</at> 请协助处理'
            })
        }
        
        result = handler.parse_message_content(message)
        
        # 验证所有@提及都被清理
        assert "<at" not in result
        assert "ou_123" not in result
        assert "ou_456" not in result
        assert "请协助处理" in result
    
    def test_parse_empty_text_message_error_handling(self, handler):
        """测试空文本消息的错误处理"""
        # 测试完全空的文本
        message_empty = {
            "message_type": "text",
            "content": json.dumps({"text": ""})
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message_empty)
        
        # 验证错误消息与原始实现一致
        assert "消息内容为空" in str(exc_info.value)
        
        # 测试只包含空格的文本
        message_whitespace = {
            "message_type": "text",
            "content": json.dumps({"text": "   "})
        }
        
        # 空格会被清理，导致内容为空
        # 但由于清理发生在返回之前，这个测试应该返回空字符串或抛出错误
        # 根据当前实现，空格不会被视为空内容，所以会返回清理后的空字符串
        result = handler.parse_message_content(message_whitespace)
        assert result == ""
    
    def test_parse_text_message_with_only_mentions(self, handler):
        """测试只包含@提及的文本消息"""
        message = {
            "message_type": "text",
            "content": json.dumps({"text": '<at user_id="ou_123">张三</at>'})
        }
        
        result = handler.parse_message_content(message)
        
        # 验证清理后的结果为空字符串
        assert result == ""
    
    def test_parse_text_message_event_message_format(self, handler):
        """测试 EventMessage 对象格式的文本消息"""
        # 创建模拟的 EventMessage 对象
        event_message = Mock()
        event_message.message_type = "text"
        event_message.content = json.dumps({"text": "使用 EventMessage 格式的文本消息"})
        
        result = handler.parse_message_content(event_message)
        
        # 验证返回值与字典格式一致
        assert result == "使用 EventMessage 格式的文本消息"
    
    def test_parse_text_message_dict_format(self, handler):
        """测试字典格式的文本消息"""
        message = {
            "message_type": "text",
            "content": json.dumps({"text": "使用字典格式的文本消息"})
        }
        
        result = handler.parse_message_content(message)
        
        # 验证返回值正确
        assert result == "使用字典格式的文本消息"
    
    def test_parse_text_message_both_formats_produce_same_result(self, handler):
        """测试文本消息的两种格式产生相同的结果"""
        text_content = "测试格式兼容性的文本消息"
        
        # EventMessage 对象格式
        event_message = Mock()
        event_message.message_type = "text"
        event_message.content = json.dumps({"text": text_content})
        
        # 字典格式
        dict_message = {
            "message_type": "text",
            "content": json.dumps({"text": text_content})
        }
        
        result_event = handler.parse_message_content(event_message)
        result_dict = handler.parse_message_content(dict_message)
        
        # 验证两种格式产生相同的结果
        assert result_event == result_dict
        assert result_event == text_content
    
    def test_parse_text_message_with_special_characters(self, handler):
        """测试包含特殊字符的文本消息"""
        message = {
            "message_type": "text",
            "content": json.dumps({"text": "特殊字符测试：!@#$%^&*()_+-=[]{}|;':\",./<>?"})
        }
        
        result = handler.parse_message_content(message)
        
        # 验证特殊字符被正确保留
        assert result == "特殊字符测试：!@#$%^&*()_+-=[]{}|;':\",./<>?"
    
    def test_parse_text_message_with_newlines(self, handler):
        """测试包含换行符的文本消息"""
        message = {
            "message_type": "text",
            "content": json.dumps({"text": "第一行\n第二行\n第三行"})
        }
        
        result = handler.parse_message_content(message)
        
        # 验证换行符被 _clean_mentions 方法转换为空格（这是原始实现的行为）
        # _clean_mentions 使用 re.sub(r'\s+', ' ', text) 将所有连续空白字符替换为单个空格
        assert result == "第一行 第二行 第三行"
        assert "\n" not in result
    
    def test_parse_text_message_with_unicode(self, handler):
        """测试包含 Unicode 字符的文本消息"""
        message = {
            "message_type": "text",
            "content": json.dumps({"text": "Unicode 测试：😀 🎉 ✨ 中文 日本語 한국어"})
        }
        
        result = handler.parse_message_content(message)
        
        # 验证 Unicode 字符被正确保留
        assert result == "Unicode 测试：😀 🎉 ✨ 中文 日本語 한국어"
    
    def test_parse_text_message_invalid_json_error_handling(self, handler):
        """测试文本消息的无效 JSON 错误处理"""
        message = {
            "message_type": "text",
            "content": "invalid json {not valid}"
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        # 验证错误消息与原始实现一致
        assert "JSON 解析失败" in str(exc_info.value)
    
    def test_parse_text_message_missing_text_field(self, handler):
        """测试缺少 text 字段的文本消息"""
        message = {
            "message_type": "text",
            "content": json.dumps({"other_field": "value"})
        }
        
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        
        # 验证错误消息
        assert "消息内容为空" in str(exc_info.value)
    
    def test_parse_text_message_long_content(self, handler):
        """测试长文本消息"""
        long_text = "这是一条很长的消息。" * 100  # 创建一个长文本
        message = {
            "message_type": "text",
            "content": json.dumps({"text": long_text})
        }
        
        result = handler.parse_message_content(message)
        
        # 验证长文本被正确处理
        assert result == long_text
        assert len(result) == len(long_text)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
