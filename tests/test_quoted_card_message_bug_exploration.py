"""
引用卡片消息Bug条件探索性测试

此测试用于在未修复的代码上暴露反例，演示bug的存在。
测试编码了期望行为 - 在实现修复后通过时将验证修复正确。

关键: 此测试必须在未修复代码上失败 - 失败确认bug存在
不要在测试失败时尝试修复测试或代码
"""
import json
import pytest
from unittest.mock import Mock
from feishu_bot.message_handler import MessageHandler
from feishu_bot.cache import DeduplicationCache


class TestQuotedCardMessageBugExploration:
    """引用卡片消息Bug条件探索性测试类"""
    
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
    
    def test_card_with_header_and_elements(self, handler, mock_client):
        """
        Property 1: Fault Condition - 卡片消息内容提取不完整
        测试用例1: 包含header和elements的卡片（应提取标题和所有文本内容）
        
        **Validates: Requirements 1.1, 2.1, 2.2, 2.3**
        
        期望行为: 提取的内容应包含标题和elements中的所有文本
        当前行为（bug）: 仅返回标题，忽略elements中的内容
        """
        # 构造包含header和elements的卡片消息
        card_content = {
            "header": {
                "title": {
                    "content": "错误通知"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": "AttributeError: 'NoneType' object has no attribute 'get'"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": "文件: api/handler.py"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": "行号: 42"
                    }
                }
            ]
        }
        
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_response.data.message.message_type = "interactive"
        mock_response.data.message.content = json.dumps(card_content)
        
        mock_client.im.v1.message.get.return_value = mock_response
        
        # 调用方法
        result = handler.get_quoted_message("msg_123")
        
        # 验证结果包含所有内容
        assert result is not None, "结果不应为None"
        assert result.startswith("[卡片消息]"), "结果应以[卡片消息]开头"
        
        # 验证包含标题
        assert "错误通知" in result, "结果应包含标题"
        
        # 验证包含elements中的所有文本内容（这是bug - 当前代码会失败）
        assert "AttributeError" in result, "结果应包含错误类型"
        assert "api/handler.py" in result, "结果应包含文件名"
        assert "行号: 42" in result, "结果应包含行号"
    
    def test_card_with_elements_only(self, handler, mock_client):
        """
        Property 1: Fault Condition - 卡片消息内容提取不完整
        测试用例2: 仅包含elements的卡片（应提取所有文本内容）
        
        **Validates: Requirements 1.2, 2.1, 2.2, 2.3**
        
        期望行为: 提取的内容应包含elements中的所有文本
        当前行为（bug）: 返回通用字符串"[卡片消息]"，不包含任何实际内容
        """
        # 构造仅包含elements的卡片消息（无header）
        card_content = {
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": "任务已完成"
                    }
                },
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "查看详情"
                    }
                }
            ]
        }
        
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_response.data.message.message_type = "interactive"
        mock_response.data.message.content = json.dumps(card_content)
        
        mock_client.im.v1.message.get.return_value = mock_response
        
        # 调用方法
        result = handler.get_quoted_message("msg_123")
        
        # 验证结果包含所有内容
        assert result is not None, "结果不应为None"
        assert result.startswith("[卡片消息]"), "结果应以[卡片消息]开头"
        
        # 验证包含elements中的所有文本内容（这是bug - 当前代码会失败）
        assert "任务已完成" in result, "结果应包含任务状态文本"
        assert "查看详情" in result, "结果应包含按钮文本"
    
    def test_card_with_nested_structure(self, handler, mock_client):
        """
        Property 1: Fault Condition - 卡片消息内容提取不完整
        测试用例3: 包含嵌套结构的卡片（column_set、fields）
        
        **Validates: Requirements 1.4, 2.1, 2.2, 2.3**
        
        期望行为: 提取的内容应包含嵌套结构中的所有文本
        当前行为（bug）: 忽略嵌套结构中的内容
        """
        # 构造包含嵌套结构的卡片消息
        card_content = {
            "header": {
                "title": {
                    "content": "数据报告"
                }
            },
            "elements": [
                {
                    "tag": "column_set",
                    "columns": [
                        {
                            "tag": "column",
                            "elements": [
                                {
                                    "tag": "div",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": "用户数: 1234"
                                    }
                                }
                            ]
                        },
                        {
                            "tag": "column",
                            "elements": [
                                {
                                    "tag": "div",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": "活跃率: 85%"
                                    }
                                }
                            ]
                        }
                    ]
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "plain_text",
                                "content": "增长率: 12%"
                            }
                        }
                    ]
                }
            ]
        }
        
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_response.data.message.message_type = "interactive"
        mock_response.data.message.content = json.dumps(card_content)
        
        mock_client.im.v1.message.get.return_value = mock_response
        
        # 调用方法
        result = handler.get_quoted_message("msg_123")
        
        # 验证结果包含所有内容
        assert result is not None, "结果不应为None"
        assert result.startswith("[卡片消息]"), "结果应以[卡片消息]开头"
        
        # 验证包含标题
        assert "数据报告" in result, "结果应包含标题"
        
        # 验证包含嵌套结构中的所有文本内容（这是bug - 当前代码会失败）
        assert "用户数: 1234" in result, "结果应包含用户数"
        assert "活跃率: 85%" in result, "结果应包含活跃率"
        assert "增长率: 12%" in result, "结果应包含增长率"
    
    def test_card_with_multiple_element_types(self, handler, mock_client):
        """
        Property 1: Fault Condition - 卡片消息内容提取不完整
        测试用例4: 包含多种元素类型的卡片（text、button、url_preview）
        
        **Validates: Requirements 1.3, 2.1, 2.2, 2.3**
        
        期望行为: 提取的内容应包含所有类型元素的文本
        当前行为（bug）: 忽略elements中的所有内容
        """
        # 构造包含多种元素类型的卡片消息
        card_content = {
            "header": {
                "title": {
                    "content": "项目更新"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "markdown",
                        "content": "**重要更新**: 项目已进入测试阶段"
                    }
                },
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "查看进度"
                    },
                    "url": "https://example.com/progress"
                },
                {
                    "tag": "url_preview",
                    "title": "相关文档",
                    "description": "查看完整的项目文档和API参考"
                }
            ]
        }
        
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_response.data.message.message_type = "interactive"
        mock_response.data.message.content = json.dumps(card_content)
        
        mock_client.im.v1.message.get.return_value = mock_response
        
        # 调用方法
        result = handler.get_quoted_message("msg_123")
        
        # 验证结果包含所有内容
        assert result is not None, "结果不应为None"
        assert result.startswith("[卡片消息]"), "结果应以[卡片消息]开头"
        
        # 验证包含标题
        assert "项目更新" in result, "结果应包含标题"
        
        # 验证包含不同类型元素的文本内容（这是bug - 当前代码会失败）
        assert "重要更新" in result or "项目已进入测试阶段" in result, "结果应包含markdown文本"
        assert "查看进度" in result, "结果应包含按钮文本"
        assert "相关文档" in result, "结果应包含url_preview标题"
        assert "查看完整的项目文档" in result or "API参考" in result, "结果应包含url_preview描述"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
