"""
属性测试：私聊消息发送策略

Feature: feishu-ai-bot
Property 14: 私聊消息发送策略
Validates: Requirements 6.1

测试 MessageSender 在私聊场景下的消息发送行为。
"""
import pytest
from hypothesis import given, strategies as st
from unittest.mock import Mock, MagicMock
from feishu_bot.message_sender import MessageSender


# 生成有效的聊天 ID 和消息内容
@st.composite
def valid_chat_data(draw):
    """生成有效的聊天数据"""
    chat_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=33, max_codepoint=126
    )))
    content = draw(st.text(min_size=1, max_size=500))
    return chat_id, content


@given(valid_chat_data())
def test_p2p_chat_sends_new_message(chat_data):
    """
    Property 14: 私聊消息发送策略
    
    For any chat_type 为 "p2p" 的消息，Message_Sender 应该使用 
    im.v1.message.create API 发送新消息到指定的 chat_id。
    
    Validates: Requirements 6.1
    """
    chat_id, content = chat_data
    
    # 创建 mock 客户端
    mock_client = Mock()
    mock_response = Mock()
    mock_response.success.return_value = True
    mock_client.im.v1.message.create.return_value = mock_response
    
    # 创建消息发送器
    sender = MessageSender(mock_client)
    
    # 发送私聊消息
    result = sender.send_message(
        chat_type="p2p",
        chat_id=chat_id,
        message_id="dummy_message_id",  # 私聊不使用此参数
        content=content
    )
    
    # 验证结果
    assert result is True, "私聊消息发送应该成功"
    
    # 验证调用了 create 方法而不是 reply 方法
    assert mock_client.im.v1.message.create.called, \
        "私聊应该调用 create 方法发送新消息"
    assert not mock_client.im.v1.message.reply.called, \
        "私聊不应该调用 reply 方法"
    
    # 验证传递的参数
    call_args = mock_client.im.v1.message.create.call_args
    request = call_args[0][0]
    
    # 验证 receive_id_type 为 chat_id
    assert hasattr(request, 'receive_id_type'), "请求应该包含 receive_id_type"
    
    # 验证请求体包含正确的 chat_id
    request_body = request.body
    assert request_body.receive_id == chat_id, \
        f"接收者 ID 应该是 {chat_id}"
    assert request_body.msg_type == "text", \
        "消息类型应该是 text"


@given(st.text(min_size=1, max_size=50))
def test_p2p_message_not_using_reply(chat_id):
    """
    验证私聊消息不使用 reply 方法
    
    For any p2p 消息，即使提供了 message_id，也应该使用 create 而不是 reply。
    
    Validates: Requirements 6.1
    """
    mock_client = Mock()
    mock_response = Mock()
    mock_response.success.return_value = True
    mock_client.im.v1.message.create.return_value = mock_response
    
    sender = MessageSender(mock_client)
    
    # 发送私聊消息（提供 message_id）
    sender.send_message(
        chat_type="p2p",
        chat_id=chat_id,
        message_id="some_message_id",
        content="test content"
    )
    
    # 验证没有调用 reply 方法
    assert not mock_client.im.v1.message.reply.called, \
        "私聊消息不应该使用 reply 方法，即使提供了 message_id"
