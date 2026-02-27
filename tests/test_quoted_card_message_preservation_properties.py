"""
引用卡片消息修复 - 保持不变属性测试

此测试验证修复不会影响现有的非卡片消息处理行为。
遵循观察优先方法：首先在未修复代码上观察行为，然后编写测试捕获该行为。

Property 2: Preservation - 非卡片消息处理行为
对于任何引用消息类型不是"interactive"的输入，修复后的代码应产生与原始代码完全相同的行为。

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**
"""
import json
import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock
from feishu_bot.message_handler import MessageHandler
from feishu_bot.cache import DeduplicationCache


# ============================================================================
# 策略定义
# ============================================================================

# 生成有效的文本内容
valid_text_strategy = st.text(
    min_size=1,
    max_size=1000,
    alphabet=st.characters(
        blacklist_categories=('Cs',),  # 排除代理字符
        blacklist_characters=('\x00',)  # 排除空字符
    )
)

# 生成非interactive和非text的消息类型
other_message_types = st.sampled_from([
    "image", "file", "audio", "media", "sticker",
    "share_chat", "share_user", "system", "post"
])


# ============================================================================
# Property 2.1: 文本消息处理保持不变
# **Validates: Requirements 3.1**
# ============================================================================

@settings(max_examples=100)
@given(text_content=valid_text_strategy)
def test_preservation_text_message_extraction(text_content):
    """
    Property 2.1: 文本消息处理保持不变
    
    对于任何文本消息（message_type="text"），修复后的代码应继续正确提取
    text字段内容，行为与原始代码完全相同。
    
    **Validates: Requirements 3.1**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造文本消息的API响应
    mock_response = Mock()
    mock_response.success.return_value = True
    mock_response.data.message.message_type = "text"
    mock_response.data.message.content = json.dumps({"text": text_content})
    
    mock_client.im.v1.message.get.return_value = mock_response
    
    # 调用方法
    result = handler.get_quoted_message("msg_123")
    
    # 验证结果与原始文本完全相同
    assert result == text_content, \
        f"Text message extraction should return exact text content. Expected: {text_content}, Got: {result}"
    
    # 验证不包含卡片消息格式前缀（只有当文本不是以"["开头时才检查）
    if not text_content.startswith("["):
        assert not result.startswith("[卡片消息]"), \
            "Text message should not have '[卡片消息]' prefix"


@settings(max_examples=100)
@given(
    text_content=st.text(
        min_size=1,
        max_size=500,
        alphabet=st.characters(
            whitelist_categories=('Lo',),  # 中文字符
            min_codepoint=0x4E00,
            max_codepoint=0x9FFF
        )
    )
)
def test_preservation_text_message_chinese(text_content):
    """
    Property 2.1: 文本消息处理保持不变（中文）
    
    对于任何包含中文的文本消息，修复后的代码应继续正确提取内容。
    
    **Validates: Requirements 3.1**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造文本消息的API响应
    mock_response = Mock()
    mock_response.success.return_value = True
    mock_response.data.message.message_type = "text"
    mock_response.data.message.content = json.dumps({"text": text_content})
    
    mock_client.im.v1.message.get.return_value = mock_response
    
    # 调用方法
    result = handler.get_quoted_message("msg_123")
    
    # 验证结果与原始文本完全相同
    assert result == text_content, \
        f"Chinese text message should be extracted correctly. Expected: {text_content}, Got: {result}"


@settings(max_examples=100)
@given(
    text_content=valid_text_strategy,
    call_count=st.integers(min_value=2, max_value=5)
)
def test_preservation_text_message_idempotent(text_content, call_count):
    """
    Property 2.1: 文本消息处理保持不变（幂等性）
    
    对于任何文本消息，多次调用应返回相同结果（幂等性）。
    
    **Validates: Requirements 3.1**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造文本消息的API响应
    mock_response = Mock()
    mock_response.success.return_value = True
    mock_response.data.message.message_type = "text"
    mock_response.data.message.content = json.dumps({"text": text_content})
    
    mock_client.im.v1.message.get.return_value = mock_response
    
    # 多次调用
    results = []
    for _ in range(call_count):
        result = handler.get_quoted_message("msg_123")
        results.append(result)
    
    # 验证所有结果相同
    assert len(set(results)) == 1, \
        f"Multiple calls should return the same result. Got: {results}"
    
    # 验证结果正确
    assert results[0] == text_content, \
        f"Result should match text content. Expected: {text_content}, Got: {results[0]}"


# ============================================================================
# Property 2.2: 其他消息类型处理保持不变
# **Validates: Requirements 3.2**
# ============================================================================

@settings(max_examples=100)
@given(message_type=other_message_types)
def test_preservation_other_message_types(message_type):
    """
    Property 2.2: 其他消息类型处理保持不变
    
    对于任何非text和非interactive的消息类型，修复后的代码应继续返回
    "[{message_type} 消息]"格式的字符串。
    
    **Validates: Requirements 3.2**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造其他类型消息的API响应
    mock_response = Mock()
    mock_response.success.return_value = True
    mock_response.data.message.message_type = message_type
    mock_response.data.message.content = json.dumps({"data": "some_data"})
    
    mock_client.im.v1.message.get.return_value = mock_response
    
    # 调用方法
    result = handler.get_quoted_message("msg_123")
    
    # 验证返回格式
    expected = f"[{message_type} 消息]"
    assert result == expected, \
        f"Other message types should return '[{{type}} 消息]' format. Expected: {expected}, Got: {result}"


@settings(max_examples=100)
@given(
    message_type=other_message_types,
    content_data=st.dictionaries(
        keys=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=ord('a'), max_codepoint=ord('z'))),
        values=st.one_of(st.text(max_size=100), st.integers(), st.booleans())
    )
)
def test_preservation_other_message_types_with_content(message_type, content_data):
    """
    Property 2.2: 其他消息类型处理保持不变（包含内容）
    
    对于任何非text和非interactive的消息类型，无论content字段包含什么数据，
    都应返回"[{message_type} 消息]"格式。
    
    **Validates: Requirements 3.2**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造其他类型消息的API响应
    mock_response = Mock()
    mock_response.success.return_value = True
    mock_response.data.message.message_type = message_type
    mock_response.data.message.content = json.dumps(content_data)
    
    mock_client.im.v1.message.get.return_value = mock_response
    
    # 调用方法
    result = handler.get_quoted_message("msg_123")
    
    # 验证返回格式（不受content影响）
    expected = f"[{message_type} 消息]"
    assert result == expected, \
        f"Other message types should return '[{{type}} 消息]' format regardless of content. Expected: {expected}, Got: {result}"


@settings(max_examples=100)
@given(
    message_type=other_message_types,
    call_count=st.integers(min_value=2, max_value=5)
)
def test_preservation_other_message_types_idempotent(message_type, call_count):
    """
    Property 2.2: 其他消息类型处理保持不变（幂等性）
    
    对于任何其他消息类型，多次调用应返回相同结果。
    
    **Validates: Requirements 3.2**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造其他类型消息的API响应
    mock_response = Mock()
    mock_response.success.return_value = True
    mock_response.data.message.message_type = message_type
    mock_response.data.message.content = json.dumps({})
    
    mock_client.im.v1.message.get.return_value = mock_response
    
    # 多次调用
    results = []
    for _ in range(call_count):
        result = handler.get_quoted_message("msg_123")
        results.append(result)
    
    # 验证所有结果相同
    assert len(set(results)) == 1, \
        f"Multiple calls should return the same result. Got: {results}"
    
    # 验证结果格式正确
    expected = f"[{message_type} 消息]"
    assert results[0] == expected, \
        f"Result should match expected format. Expected: {expected}, Got: {results[0]}"


# ============================================================================
# Property 2.3: API错误处理保持不变
# **Validates: Requirements 3.3**
# ============================================================================

@settings(max_examples=100)
@given(
    error_code=st.integers(min_value=400, max_value=599),
    error_msg=st.text(min_size=1, max_size=100)
)
def test_preservation_api_failure_returns_none(error_code, error_msg):
    """
    Property 2.3: API错误处理保持不变
    
    对于任何API调用失败的情况，修复后的代码应继续返回None，
    保持现有的错误处理逻辑。
    
    **Validates: Requirements 3.3**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 模拟API失败响应
    mock_response = Mock()
    mock_response.success.return_value = False
    mock_response.code = error_code
    mock_response.msg = error_msg
    mock_response.get_log_id.return_value = "log_123"
    
    mock_client.im.v1.message.get.return_value = mock_response
    
    # 调用方法
    result = handler.get_quoted_message("msg_123")
    
    # 验证返回None
    assert result is None, \
        f"API failure should return None. Got: {result}"


@settings(max_examples=100)
@given(
    exception_type=st.sampled_from([
        Exception, RuntimeError, ValueError, ConnectionError, TimeoutError
    ]),
    exception_msg=st.text(min_size=1, max_size=100)
)
def test_preservation_api_exception_returns_none(exception_type, exception_msg):
    """
    Property 2.3: API错误处理保持不变（异常）
    
    对于任何API调用抛出异常的情况，修复后的代码应继续返回None。
    
    **Validates: Requirements 3.3**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 模拟API抛出异常
    mock_client.im.v1.message.get.side_effect = exception_type(exception_msg)
    
    # 调用方法
    result = handler.get_quoted_message("msg_123")
    
    # 验证返回None
    assert result is None, \
        f"API exception should return None. Got: {result}"


@settings(max_examples=100)
@given(empty_parent_id=st.sampled_from(["", None]))
def test_preservation_empty_parent_id_returns_none(empty_parent_id):
    """
    Property 2.3: API错误处理保持不变（空parent_id）
    
    对于空的parent_id，修复后的代码应继续返回None。
    
    **Validates: Requirements 3.3**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 调用方法
    result = handler.get_quoted_message(empty_parent_id)
    
    # 验证返回None
    assert result is None, \
        f"Empty parent_id should return None. Got: {result}"
    
    # 验证没有调用API
    mock_client.im.v1.message.get.assert_not_called()


# ============================================================================
# Property 2.4: 消息组合逻辑保持不变
# **Validates: Requirements 3.4**
# ============================================================================

@settings(max_examples=100)
@given(
    quoted_text=valid_text_strategy,
    current_text=valid_text_strategy
)
def test_preservation_combine_messages_format(quoted_text, current_text):
    """
    Property 2.4: 消息组合逻辑保持不变
    
    对于任何引用消息和当前消息，修复后的combine_messages方法应继续使用
    "引用消息：{quoted}\n\n当前消息：{current}"的格式组合消息。
    
    **Validates: Requirements 3.4**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 调用方法
    result = handler.combine_messages(quoted_text, current_text)
    
    # 验证格式
    expected = f"引用消息：{quoted_text}\n\n当前消息：{current_text}"
    assert result == expected, \
        f"combine_messages format should remain unchanged. Expected: {expected}, Got: {result}"
    
    # 验证包含引用消息
    assert quoted_text in result, \
        f"Combined message should contain quoted text: {quoted_text}"
    
    # 验证包含当前消息
    assert current_text in result, \
        f"Combined message should contain current text: {current_text}"
    
    # 验证分隔符
    assert "\n\n" in result, \
        "Combined message should contain separator '\\n\\n'"


@settings(max_examples=100)
@given(current_text=valid_text_strategy)
def test_preservation_combine_messages_no_quote(current_text):
    """
    Property 2.4: 消息组合逻辑保持不变（无引用）
    
    对于没有引用消息的情况（None），修复后的combine_messages方法应继续
    只返回当前消息，不添加任何前缀。
    
    **Validates: Requirements 3.4**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 调用方法
    result = handler.combine_messages(None, current_text)
    
    # 验证只返回当前消息
    assert result == current_text, \
        f"Without quoted message, should return current text only. Expected: {current_text}, Got: {result}"
    
    # 验证不包含格式前缀
    assert not result.startswith("引用消息："), \
        "Without quoted message, should not have '引用消息：' prefix"


@settings(max_examples=100)
@given(
    quoted_text=valid_text_strategy,
    current_text=valid_text_strategy,
    call_count=st.integers(min_value=2, max_value=5)
)
def test_preservation_combine_messages_idempotent(quoted_text, current_text, call_count):
    """
    Property 2.4: 消息组合逻辑保持不变（幂等性）
    
    对于任何引用消息和当前消息，多次调用combine_messages应返回相同结果。
    
    **Validates: Requirements 3.4**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 多次调用
    results = []
    for _ in range(call_count):
        result = handler.combine_messages(quoted_text, current_text)
        results.append(result)
    
    # 验证所有结果相同
    assert len(set(results)) == 1, \
        f"Multiple calls should return the same result. Got: {results}"
    
    # 验证结果格式正确
    expected = f"引用消息：{quoted_text}\n\n当前消息：{current_text}"
    assert results[0] == expected, \
        f"Result should match expected format. Expected: {expected}, Got: {results[0]}"


@settings(max_examples=100)
@given(
    quoted_text=valid_text_strategy,
    current_text=valid_text_strategy
)
def test_preservation_combine_messages_order(quoted_text, current_text):
    """
    Property 2.4: 消息组合逻辑保持不变（顺序）
    
    对于任何引用消息和当前消息，组合后的消息应先显示引用消息，后显示当前消息。
    
    **Validates: Requirements 3.4**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 调用方法
    result = handler.combine_messages(quoted_text, current_text)
    
    # 查找引用消息和当前消息的位置
    quoted_marker = "引用消息："
    current_marker = "当前消息："
    
    quoted_pos = result.find(quoted_marker)
    current_pos = result.find(current_marker)
    
    # 验证引用消息在前
    assert quoted_pos < current_pos, \
        f"Quoted message should appear before current message. Quoted pos: {quoted_pos}, Current pos: {current_pos}"


# ============================================================================
# 综合测试：验证修复不影响整体工作流
# ============================================================================

@settings(max_examples=50)
@given(
    message_type=st.sampled_from(["text", "image", "file", "audio"]),
    text_content=valid_text_strategy,
    current_message=valid_text_strategy
)
def test_preservation_end_to_end_workflow(message_type, text_content, current_message):
    """
    综合测试：验证修复不影响整体工作流
    
    对于任何非interactive的消息类型，从获取引用消息到组合消息的完整流程
    应保持不变。
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造API响应
    mock_response = Mock()
    mock_response.success.return_value = True
    mock_response.data.message.message_type = message_type
    
    if message_type == "text":
        mock_response.data.message.content = json.dumps({"text": text_content})
        expected_quoted = text_content
    else:
        mock_response.data.message.content = json.dumps({"data": "some_data"})
        expected_quoted = f"[{message_type} 消息]"
    
    mock_client.im.v1.message.get.return_value = mock_response
    
    # 获取引用消息
    quoted = handler.get_quoted_message("msg_123")
    
    # 验证引用消息正确
    assert quoted == expected_quoted, \
        f"Quoted message should match expected. Expected: {expected_quoted}, Got: {quoted}"
    
    # 组合消息
    combined = handler.combine_messages(quoted, current_message)
    
    # 验证组合消息格式正确
    expected_combined = f"引用消息：{expected_quoted}\n\n当前消息：{current_message}"
    assert combined == expected_combined, \
        f"Combined message should match expected format. Expected: {expected_combined}, Got: {combined}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
