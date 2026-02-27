"""
消息处理器属性测试
使用 Hypothesis 进行基于属性的测试
"""
import json
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock
from feishu_bot.message_handler import MessageHandler
from feishu_bot.cache import DeduplicationCache


# 定义策略：生成有效的文本内容
valid_text_strategy = st.text(min_size=1, max_size=1000)

# 定义策略：生成有效的飞书文本消息
@st.composite
def valid_text_message(draw):
    """生成有效的飞书文本消息"""
    text = draw(valid_text_strategy)
    return {
        "message_type": "text",
        "content": json.dumps({"text": text})
    }


# Feature: feishu-ai-bot, Property 1: 文本消息内容提取
# **Validates: Requirements 1.1**
@settings(max_examples=100)
@given(message=valid_text_message())
def test_text_message_content_extraction(message):
    """
    Property 1: 文本消息内容提取
    
    For any 有效的飞书文本消息，Message_Handler 应该能够正确提取消息的文本内容，
    且提取的内容应该与原始消息的 text 字段相同。
    
    **Validates: Requirements 1.1**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 解析消息内容
    extracted_text = handler.parse_message_content(message)
    
    # 验证提取的文本与原始文本相同
    original_text = json.loads(message["content"])["text"]
    assert extracted_text == original_text, \
        f"Extracted text should match original text. Expected: {original_text}, Got: {extracted_text}"


# Feature: feishu-ai-bot, Property 1: 文本消息内容提取（特殊字符）
# **Validates: Requirements 1.1**
@settings(max_examples=100)
@given(
    text=st.text(
        min_size=1,
        max_size=500,
        alphabet=st.characters(
            blacklist_categories=('Cs',),  # 排除代理字符
            blacklist_characters=('\x00',)  # 排除空字符
        )
    )
)
def test_text_message_extraction_with_special_characters(text):
    """
    Property 1: 文本消息内容提取（特殊字符）
    
    For any 包含特殊字符的文本消息，Message_Handler 应该能够正确提取内容，
    包括换行符、制表符、Unicode 字符等。
    
    **Validates: Requirements 1.1**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造消息
    message = {
        "message_type": "text",
        "content": json.dumps({"text": text})
    }
    
    # 解析消息内容
    extracted_text = handler.parse_message_content(message)
    
    # 验证提取的文本与原始文本相同
    assert extracted_text == text, \
        f"Extracted text should preserve special characters. Expected: {repr(text)}, Got: {repr(extracted_text)}"


# Feature: feishu-ai-bot, Property 1: 文本消息内容提取（中英文混合）
# **Validates: Requirements 1.1**
@settings(max_examples=100)
@given(
    chinese_text=st.text(
        min_size=1,
        max_size=200,
        alphabet=st.characters(
            whitelist_categories=('Lo',),  # 中文字符
            min_codepoint=0x4E00,
            max_codepoint=0x9FFF
        )
    ),
    english_text=st.text(
        min_size=1,
        max_size=200,
        alphabet=st.characters(min_codepoint=ord('a'), max_codepoint=ord('z'))
    )
)
def test_text_message_extraction_mixed_languages(chinese_text, english_text):
    """
    Property 1: 文本消息内容提取（中英文混合）
    
    For any 包含中英文混合的文本消息，Message_Handler 应该能够正确提取内容。
    
    **Validates: Requirements 1.1**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 混合中英文
    mixed_text = f"{chinese_text} {english_text}"
    
    # 构造消息
    message = {
        "message_type": "text",
        "content": json.dumps({"text": mixed_text})
    }
    
    # 解析消息内容
    extracted_text = handler.parse_message_content(message)
    
    # 验证提取的文本与原始文本相同
    assert extracted_text == mixed_text, \
        f"Extracted text should preserve mixed languages. Expected: {mixed_text}, Got: {extracted_text}"


# Feature: feishu-ai-bot, Property 1: 文本消息内容提取（幂等性）
# **Validates: Requirements 1.1**
@settings(max_examples=100)
@given(
    message=valid_text_message(),
    parse_count=st.integers(min_value=1, max_value=10)
)
def test_text_message_extraction_idempotent(message, parse_count):
    """
    Property 1: 文本消息内容提取（幂等性）
    
    For any 有效的文本消息，多次解析应该返回相同的结果（幂等性）。
    
    **Validates: Requirements 1.1**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 多次解析消息
    results = []
    for _ in range(parse_count):
        extracted_text = handler.parse_message_content(message)
        results.append(extracted_text)
    
    # 验证所有结果相同
    assert len(set(results)) == 1, \
        f"Multiple parses should return the same result. Got: {results}"
    
    # 验证结果与原始文本相同
    original_text = json.loads(message["content"])["text"]
    assert results[0] == original_text, \
        f"Extracted text should match original text. Expected: {original_text}, Got: {results[0]}"


# Feature: feishu-ai-bot, Property 1: 文本消息内容提取（空白字符保留）
# **Validates: Requirements 1.1**
@settings(max_examples=100)
@given(
    prefix_spaces=st.integers(min_value=0, max_value=10),
    suffix_spaces=st.integers(min_value=0, max_value=10),
    text=st.text(min_size=1, max_size=100)
)
def test_text_message_extraction_preserves_whitespace(prefix_spaces, suffix_spaces, text):
    """
    Property 1: 文本消息内容提取（空白字符保留）
    
    For any 包含前后空白字符的文本消息，Message_Handler 应该保留这些空白字符。
    
    **Validates: Requirements 1.1**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 添加前后空格
    text_with_spaces = " " * prefix_spaces + text + " " * suffix_spaces
    
    # 构造消息
    message = {
        "message_type": "text",
        "content": json.dumps({"text": text_with_spaces})
    }
    
    # 解析消息内容
    extracted_text = handler.parse_message_content(message)
    
    # 验证空白字符被保留
    assert extracted_text == text_with_spaces, \
        f"Whitespace should be preserved. Expected: {repr(text_with_spaces)}, Got: {repr(extracted_text)}"
    assert len(extracted_text) == len(text_with_spaces), \
        f"Length should match. Expected: {len(text_with_spaces)}, Got: {len(extracted_text)}"


# Feature: feishu-ai-bot, Property 2: 引用消息内容组合
# **Validates: Requirements 1.2, 1.4**
@settings(max_examples=100)
@given(
    quoted_text=st.one_of(st.none(), valid_text_strategy),
    current_text=valid_text_strategy
)
def test_quoted_message_combination(quoted_text, current_text):
    """
    Property 2: 引用消息内容组合
    
    For any 有效的引用消息和当前消息，Message_Handler 应该将两者组合成
    格式为 "引用消息：{quoted}\n\n当前消息：{current}" 的字符串。
    
    **Validates: Requirements 1.2, 1.4**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 组合消息
    combined = handler.combine_messages(quoted_text, current_text)
    
    # 验证组合格式
    if quoted_text:
        expected = f"引用消息：{quoted_text}\n\n当前消息：{current_text}"
        assert combined == expected, \
            f"Combined message format incorrect. Expected: {expected}, Got: {combined}"
        
        # 验证包含引用消息
        assert quoted_text in combined, \
            f"Combined message should contain quoted text: {quoted_text}"
        
        # 验证包含当前消息
        assert current_text in combined, \
            f"Combined message should contain current text: {current_text}"
        
        # 验证分隔符
        assert "\n\n" in combined, \
            "Combined message should contain separator '\\n\\n'"
        
        # 验证前缀
        assert combined.startswith("引用消息："), \
            "Combined message should start with '引用消息：'"
        
        # 验证中间部分
        assert "当前消息：" in combined, \
            "Combined message should contain '当前消息：'"
    else:
        # 无引用消息时，应该只返回当前消息
        assert combined == current_text, \
            f"Without quoted message, should return current text only. Expected: {current_text}, Got: {combined}"


# Feature: feishu-ai-bot, Property 2: 引用消息内容组合（特殊字符）
# **Validates: Requirements 1.2, 1.4**
@settings(max_examples=100)
@given(
    quoted_text=st.text(
        min_size=1,
        max_size=500,
        alphabet=st.characters(
            blacklist_categories=('Cs',),
            blacklist_characters=('\x00',)
        )
    ),
    current_text=st.text(
        min_size=1,
        max_size=500,
        alphabet=st.characters(
            blacklist_categories=('Cs',),
            blacklist_characters=('\x00',)
        )
    )
)
def test_quoted_message_combination_special_characters(quoted_text, current_text):
    """
    Property 2: 引用消息内容组合（特殊字符）
    
    For any 包含特殊字符的引用消息和当前消息，组合后的消息应该保留所有特殊字符。
    
    **Validates: Requirements 1.2, 1.4**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 组合消息
    combined = handler.combine_messages(quoted_text, current_text)
    
    # 验证格式
    expected = f"引用消息：{quoted_text}\n\n当前消息：{current_text}"
    assert combined == expected, \
        f"Special characters should be preserved. Expected: {repr(expected)}, Got: {repr(combined)}"


# Feature: feishu-ai-bot, Property 2: 引用消息内容组合（长度保持）
# **Validates: Requirements 1.2, 1.4**
@settings(max_examples=100)
@given(
    quoted_text=valid_text_strategy,
    current_text=valid_text_strategy
)
def test_quoted_message_combination_length(quoted_text, current_text):
    """
    Property 2: 引用消息内容组合（长度保持）
    
    For any 引用消息和当前消息，组合后的消息长度应该等于两者长度之和加上格式字符的长度。
    
    **Validates: Requirements 1.2, 1.4**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 组合消息
    combined = handler.combine_messages(quoted_text, current_text)
    
    # 计算期望长度
    # 格式: "引用消息：{quoted}\n\n当前消息：{current}"
    # 前缀: "引用消息：" (5个字符)
    # 分隔符: "\n\n" (2个字符)
    # 中间: "当前消息：" (5个字符)
    format_length = len("引用消息：") + len("\n\n") + len("当前消息：")
    expected_length = len(quoted_text) + len(current_text) + format_length
    
    assert len(combined) == expected_length, \
        f"Combined message length incorrect. Expected: {expected_length}, Got: {len(combined)}"


# Feature: feishu-ai-bot, Property 2: 引用消息内容组合（幂等性）
# **Validates: Requirements 1.2, 1.4**
@settings(max_examples=100)
@given(
    quoted_text=st.one_of(st.none(), valid_text_strategy),
    current_text=valid_text_strategy,
    combine_count=st.integers(min_value=1, max_value=10)
)
def test_quoted_message_combination_idempotent(quoted_text, current_text, combine_count):
    """
    Property 2: 引用消息内容组合（幂等性）
    
    For any 引用消息和当前消息，多次组合应该返回相同的结果（幂等性）。
    
    **Validates: Requirements 1.2, 1.4**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 多次组合消息
    results = []
    for _ in range(combine_count):
        combined = handler.combine_messages(quoted_text, current_text)
        results.append(combined)
    
    # 验证所有结果相同
    assert len(set(results)) == 1, \
        f"Multiple combines should return the same result. Got: {results}"


# Feature: feishu-ai-bot, Property 2: 引用消息内容组合（空引用消息）
# **Validates: Requirements 1.2, 1.4**
@settings(max_examples=100)
@given(current_text=valid_text_strategy)
def test_quoted_message_combination_no_quote(current_text):
    """
    Property 2: 引用消息内容组合（空引用消息）
    
    For any 当前消息，如果没有引用消息（None），应该只返回当前消息，不添加任何前缀。
    
    **Validates: Requirements 1.2, 1.4**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 组合消息（无引用）
    combined = handler.combine_messages(None, current_text)
    
    # 验证只返回当前消息
    assert combined == current_text, \
        f"Without quoted message, should return current text only. Expected: {current_text}, Got: {combined}"
    
    # 验证不包含格式前缀
    assert not combined.startswith("引用消息："), \
        "Without quoted message, should not have '引用消息：' prefix"
    
    assert "当前消息：" not in combined, \
        "Without quoted message, should not have '当前消息：' marker"


# Feature: feishu-ai-bot, Property 2: 引用消息内容组合（顺序保持）
# **Validates: Requirements 1.2, 1.4**
@settings(max_examples=100)
@given(
    quoted_text=valid_text_strategy,
    current_text=valid_text_strategy
)
def test_quoted_message_combination_order(quoted_text, current_text):
    """
    Property 2: 引用消息内容组合（顺序保持）
    
    For any 引用消息和当前消息，组合后的消息应该先显示引用消息，后显示当前消息。
    
    **Validates: Requirements 1.2, 1.4**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 组合消息
    combined = handler.combine_messages(quoted_text, current_text)
    
    # 查找引用消息和当前消息的位置
    quoted_marker = "引用消息："
    current_marker = "当前消息："
    
    quoted_pos = combined.find(quoted_marker)
    current_pos = combined.find(current_marker)
    
    # 验证引用消息在前
    assert quoted_pos < current_pos, \
        f"Quoted message should appear before current message. Quoted pos: {quoted_pos}, Current pos: {current_pos}"
    
    # 验证引用消息内容在引用标记之后
    quoted_content_start = quoted_pos + len(quoted_marker)
    assert combined[quoted_content_start:quoted_content_start + len(quoted_text)] == quoted_text, \
        "Quoted text should appear immediately after '引用消息：'"
    
    # 验证当前消息内容在当前标记之后
    current_content_start = current_pos + len(current_marker)
    assert combined[current_content_start:current_content_start + len(current_text)] == current_text, \
        "Current text should appear immediately after '当前消息：'"


# Feature: feishu-ai-bot, Property 3: 非文本消息错误处理
# **Validates: Requirements 1.3**
@settings(max_examples=100)
@given(
    message_type=st.sampled_from([
        "image", "file", "audio", "media", "sticker", 
        "share_chat", "share_user", "system"
    ])
)
def test_non_text_message_error_handling(message_type):
    """
    Property 3: 非文本消息错误处理
    
    For any 非文本类型的消息（message_type != "text" and != "interactive"），Feishu_Bot 应该返回包含
    "请发送文本消息或卡片消息" 或 "please send text message or card message" 的错误消息。
    
    **Validates: Requirements 1.3, 3.4**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造非文本消息
    message = {
        "message_type": message_type,
        "content": json.dumps({"data": "some_data"})
    }
    
    # 验证抛出 ValueError
    with pytest.raises(ValueError) as exc_info:
        handler.parse_message_content(message)
    
    # 验证错误消息包含必要的提示（更新为支持卡片消息）
    error_message = str(exc_info.value).lower()
    assert ("请发送文本消息或卡片消息" in error_message or 
            "please send text message or card message" in error_message or
            "请发送文本消息" in error_message or 
            "please send text message" in error_message), \
        f"Error message should contain message type hint. Got: {exc_info.value}"
    
    # 验证错误消息包含消息类型信息
    assert message_type in str(exc_info.value), \
        f"Error message should mention the message type '{message_type}'. Got: {exc_info.value}"


# Feature: feishu-ai-bot, Property 3: 非文本消息错误处理（空消息类型）
# **Validates: Requirements 1.3**
@settings(max_examples=100)
@given(content=st.text(min_size=0, max_size=100))
def test_non_text_message_empty_type(content):
    """
    Property 3: 非文本消息错误处理（空消息类型）
    
    For any 消息类型为空字符串或缺失的消息，应该被视为非文本消息并返回错误。
    
    **Validates: Requirements 1.3**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造空消息类型的消息
    message = {
        "message_type": "",
        "content": json.dumps({"text": content})
    }
    
    # 验证抛出 ValueError
    with pytest.raises(ValueError) as exc_info:
        handler.parse_message_content(message)
    
    # 验证错误消息包含必要的提示
    error_message = str(exc_info.value).lower()
    assert "请发送文本消息" in error_message or "please send text message" in error_message, \
        f"Error message should contain '请发送文本消息' or 'please send text message'. Got: {exc_info.value}"


# Feature: feishu-ai-bot, Property 3: 非文本消息错误处理（随机消息类型）
# **Validates: Requirements 1.3**
@settings(max_examples=100)
@given(
    message_type=st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd')  # 大写、小写、数字
        )
    ).filter(lambda x: x != "text")  # 确保不是 "text"
)
def test_non_text_message_random_type(message_type):
    """
    Property 3: 非文本消息错误处理（随机消息类型）
    
    For any 非 "text" 的消息类型字符串，应该返回错误消息。
    
    **Validates: Requirements 1.3**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造随机消息类型的消息
    message = {
        "message_type": message_type,
        "content": json.dumps({"data": "some_data"})
    }
    
    # 验证抛出 ValueError
    with pytest.raises(ValueError) as exc_info:
        handler.parse_message_content(message)
    
    # 验证错误消息包含必要的提示
    error_message = str(exc_info.value).lower()
    assert "请发送文本消息" in error_message or "please send text message" in error_message, \
        f"Error message should contain '请发送文本消息' or 'please send text message'. Got: {exc_info.value}"


# Feature: feishu-ai-bot, Property 3: 非文本消息错误处理（大小写变体）
# **Validates: Requirements 1.3**
@settings(max_examples=100)
@given(
    case_variant=st.sampled_from([
        "TEXT", "Text", "tExt", "teXt", "texT", "TExt", "TeXt", "TExT"
    ])
)
def test_non_text_message_case_variants(case_variant):
    """
    Property 3: 非文本消息错误处理（大小写变体）
    
    For any "text" 的大小写变体（除了小写 "text"），应该被视为非文本消息并返回错误。
    
    **Validates: Requirements 1.3**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造大小写变体的消息
    message = {
        "message_type": case_variant,
        "content": json.dumps({"text": "some text"})
    }
    
    # 验证抛出 ValueError
    with pytest.raises(ValueError) as exc_info:
        handler.parse_message_content(message)
    
    # 验证错误消息包含必要的提示
    error_message = str(exc_info.value).lower()
    assert "请发送文本消息" in error_message or "please send text message" in error_message, \
        f"Error message should contain '请发送文本消息' or 'please send text message'. Got: {exc_info.value}"


# Feature: feishu-ai-bot, Property 3: 非文本消息错误处理（一致性）
# **Validates: Requirements 1.3**
@settings(max_examples=100)
@given(
    message_type=st.sampled_from(["image", "file", "audio", "media"]),
    parse_count=st.integers(min_value=1, max_value=10)
)
def test_non_text_message_error_consistency(message_type, parse_count):
    """
    Property 3: 非文本消息错误处理（一致性）
    
    For any 非文本消息，多次解析应该返回相同的错误消息（一致性）。
    
    **Validates: Requirements 1.3**
    """
    # 创建 MessageHandler 实例
    mock_client = Mock()
    dedup_cache = DeduplicationCache()
    handler = MessageHandler(mock_client, dedup_cache)
    
    # 构造非文本消息
    message = {
        "message_type": message_type,
        "content": json.dumps({"data": "some_data"})
    }
    
    # 多次解析并收集错误消息
    error_messages = []
    for _ in range(parse_count):
        with pytest.raises(ValueError) as exc_info:
            handler.parse_message_content(message)
        error_messages.append(str(exc_info.value))
    
    # 验证所有错误消息相同
    assert len(set(error_messages)) == 1, \
        f"Multiple parses should return the same error message. Got: {error_messages}"
    
    # 验证错误消息包含必要的提示
    error_message = error_messages[0].lower()
    assert "请发送文本消息" in error_message or "please send text message" in error_message, \
        f"Error message should contain '请发送文本消息' or 'please send text message'. Got: {error_messages[0]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
