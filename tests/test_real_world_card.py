"""
真实世界卡片消息测试
使用从飞书官方文档获取的真实卡片结构进行测试
"""
import json
import pytest
from unittest.mock import Mock
from feishu_bot.message_handler import MessageHandler
from feishu_bot.cache import DeduplicationCache


class TestRealWorldCard:
    """真实世界卡片消息测试类"""
    
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
    
    def test_real_world_leave_approval_card(self, handler, mock_client):
        """
        测试真实的休假审批卡片消息
        这是从飞书官方文档示例中获取的真实卡片结构
        """
        # 真实的休假审批卡片结构（来自飞书官方文档）
        card_content = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": "blue",
                "title": {
                    "content": "你有一个休假申请待审批",
                    "tag": "plain_text"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": "**申请人：**\n孙宝龙",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": "**休假类型：**\n年假",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "is_short": False,
                            "text": {
                                "content": "",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": "**时间：**\n2020-4-8 至 2020-4-10（共3天）",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": "**备注：**\n因家中有急事，需往返老家，故请假",
                                "tag": "lark_md"
                            }
                        }
                    ]
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "content": "批准",
                                "tag": "plain_text"
                            },
                            "type": "primary",
                            "value": {
                                "chosen": "approve"
                            }
                        },
                        {
                            "tag": "button",
                            "text": {
                                "content": "拒绝",
                                "tag": "plain_text"
                            },
                            "type": "danger",
                            "value": {
                                "chosen": "decline"
                            }
                        }
                    ],
                    "layout": "bisected"
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
        
        # 验证结果
        assert result is not None, "结果不应为None"
        assert result.startswith("[卡片消息]"), "结果应以[卡片消息]开头"
        
        # 验证包含标题
        assert "你有一个休假申请待审批" in result, "结果应包含标题"
        
        # 验证包含所有字段内容
        assert "申请人" in result or "孙宝龙" in result, "结果应包含申请人信息"
        assert "休假类型" in result or "年假" in result, "结果应包含休假类型"
        assert "时间" in result or "2020-4-8" in result, "结果应包含时间信息"
        assert "备注" in result or "因家中有急事" in result, "结果应包含备注信息"
        
        # 验证包含按钮文本
        assert "批准" in result, "结果应包含批准按钮文本"
        assert "拒绝" in result, "结果应包含拒绝按钮文本"
        
        print(f"\n提取的完整内容:\n{result}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
