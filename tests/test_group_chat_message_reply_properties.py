"""
属性测试：群聊消息回复策略

Feature: feishu-ai-bot
Property 15: 群聊消息回复策略
Validates: Requirements 6.2

测试 MessageSender 在群聊场景下的消息回复行为。
"""
import pytest
from hypothesis import given, strategies as st
from unittest.mock import Mock
from feishu_bot.message_sender import MessageSender


# 生成有效的消息 ID 和内容
@st.composite
def valid_message_data(draw):
    """生成有效的消息数据"""
    message_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=33, max_codepoint=126
    )))
    content = draw(st.text(min_size=1, max_size=500))
    return message_id, content


# 生成非 p2p 的聊天类型
non_p2p_chat_types = st.sampled_from([
    "group",
    "topic",
    "channel",
    "unknown_type"
])


@given(non_p2p_chat_types, valid_message_data())
def test_non_p2p_chat_replies_to_message(chat_type, message_data):
    """
    Property 15: 群聊消息回复策略
    
    For any chat_type 不为 "p2p" 的消息，Message_Sender 应该使用 
    im.v1.message.reply API 回复原始消息。
    
    Validates: Requirements 6.2
    """
    message_id, content = message_data
    
    # 创建 mock 客户端
    mock_client = Mock()
    mock_response = Mock()
    mock_response.success.return_value = True
    mock_client.im.v1.message.reply.return_value = mock_response
    
    # 创建消息发送器
    sender = MessageSender(mock_client)
    
    # 发送群聊消息
    result = sender.send_message(
        chat_type=chat_type,
        chat_id="dummy_chat_id",  # 群聊不使用此参数
        message_id=message_id,
        content=content
    )
    
    # 验证结果
    assert result is True, f"群聊消息回复应该成功 (chat_type={chat_type})"
    
    # 验证调用了 reply 方法而不是 create 方法
    assert mock_client.im.v1.message.reply.called, \
        f"群聊应该调用 reply 方法回复消息 (chat_type={chat_type})"
    assert not mock_client.im.v1.message.create.called, \
        f"群聊不应该调用 create 方法 (chat_type={chat_type})"
    
    # 验证传递的参数
    call_args = mock_client.im.v1.message.reply.call_args
    request = call_args[0][0]
    
    # 验证 message_id
    assert request.message_id == message_id, \
        f"消息 ID 应该是 {message_id}"
    
    # 验证请求体
    request_body = request.body
    assert request_body.msg_type == "text", \
        "消息类型应该是 text"


@given(st.text(min_size=1, max_size=50))
def test_group_chat_uses_message_id(message_id):
    """
    验证群聊消息使用 message_id 进行回复
    
    For any 群聊消息，应该使用提供的 message_id 调用 reply 方法。
    
    Validates: Requirements 6.2
    """
    mock_client = Mock()
    mock_response = Mock()
    mock_response.success.return_value = True
    mock_client.im.v1.message.reply.return_value = mock_response
    
    sender = MessageSender(mock_client)
    
    # 发送群聊消息
    sender.send_message(
        chat_type="group",
        chat_id="dummy_chat_id",
        message_id=message_id,
        content="test content"
    )
    
    # 验证使用了正确的 message_id
    call_args = mock_client.im.v1.message.reply.call_args
    request = call_args[0][0]
    assert request.message_id == message_id, \
        f"应该使用提供的 message_id: {message_id}"


@given(non_p2p_chat_types)
def test_group_chat_not_using_create(chat_type):
    """
    验证群聊消息不使用 create 方法
    
    For any 非 p2p 消息，即使提供了 chat_id，也应该使用 reply 而不是 create。
    
    Validates: Requirements 6.2
    """
    mock_client = Mock()
    mock_response = Mock()
    mock_response.success.return_value = True
    mock_client.im.v1.message.reply.return_value = mock_response
    
    sender = MessageSender(mock_client)
    
    # 发送群聊消息（提供 chat_id）
    sender.send_message(
        chat_type=chat_type,
        chat_id="some_chat_id",
        message_id="test_message_id",
        content="test content"
    )
    
    # 验证没有调用 create 方法
    assert not mock_client.im.v1.message.create.called, \
        f"群聊消息不应该使用 create 方法 (chat_type={chat_type})"
