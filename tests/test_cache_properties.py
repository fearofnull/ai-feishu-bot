"""
消息去重缓存属性测试
使用 Hypothesis 进行基于属性的测试
"""
import pytest
from hypothesis import given, strategies as st, settings
from feishu_bot.cache import DeduplicationCache


# Feature: feishu-ai-bot, Property 4: 消息去重缓存一致性
# **Validates: Requirements 2.1, 2.3**
@settings(max_examples=100)
@given(message_id=st.text(min_size=1, max_size=100))
def test_cache_consistency_after_mark_processed(message_id):
    """
    Property 4: 消息去重缓存一致性
    
    For any 消息 ID，在调用 mark_processed 后，is_processed 应该返回 true；
    在首次处理前，is_processed 应该返回 false。
    
    **Validates: Requirements 2.1, 2.3**
    """
    cache = DeduplicationCache()
    
    # 在标记前，消息应该未被处理
    assert not cache.is_processed(message_id), \
        f"Message {message_id} should not be processed before mark_processed"
    
    # 标记消息为已处理
    cache.mark_processed(message_id)
    
    # 在标记后，消息应该被标记为已处理
    assert cache.is_processed(message_id), \
        f"Message {message_id} should be processed after mark_processed"


# Feature: feishu-ai-bot, Property 4: 消息去重缓存一致性（多次标记）
# **Validates: Requirements 2.1, 2.3**
@settings(max_examples=100)
@given(
    message_id=st.text(min_size=1, max_size=100),
    mark_count=st.integers(min_value=1, max_value=10)
)
def test_cache_consistency_multiple_marks(message_id, mark_count):
    """
    Property 4: 消息去重缓存一致性（多次标记）
    
    For any 消息 ID，无论调用 mark_processed 多少次，
    is_processed 都应该返回 true。
    
    **Validates: Requirements 2.1, 2.3**
    """
    cache = DeduplicationCache()
    
    # 多次标记同一消息
    for _ in range(mark_count):
        cache.mark_processed(message_id)
    
    # 消息应该被标记为已处理
    assert cache.is_processed(message_id), \
        f"Message {message_id} should be processed after {mark_count} mark_processed calls"


# Feature: feishu-ai-bot, Property 4: 消息去重缓存一致性（多个消息）
# **Validates: Requirements 2.1, 2.3**
@settings(max_examples=100)
@given(message_ids=st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=50, unique=True))
def test_cache_consistency_multiple_messages(message_ids):
    """
    Property 4: 消息去重缓存一致性（多个消息）
    
    For any 消息 ID 列表，所有标记为已处理的消息都应该返回 true，
    未标记的消息应该返回 false。
    
    **Validates: Requirements 2.1, 2.3**
    """
    cache = DeduplicationCache()
    
    # 标记所有消息
    for message_id in message_ids:
        cache.mark_processed(message_id)
    
    # 所有消息都应该被标记为已处理
    for message_id in message_ids:
        assert cache.is_processed(message_id), \
            f"Message {message_id} should be processed after mark_processed"
    
    # 未标记的消息应该返回 false
    unprocessed_id = "unprocessed_message_xyz_123"
    assert not cache.is_processed(unprocessed_id), \
        f"Message {unprocessed_id} should not be processed"


# Feature: feishu-ai-bot, Property 6: 缓存容量限制
# **Validates: Requirements 2.4, 2.5**
@settings(max_examples=100)
@given(
    num_messages=st.integers(min_value=1001, max_value=2000),
    max_size=st.integers(min_value=100, max_value=1000)
)
def test_cache_capacity_limit(num_messages, max_size):
    """
    Property 6: 缓存容量限制
    
    For any 超过 max_size 个消息 ID 的序列，Deduplication_Cache 应该只保留
    最新的 max_size 个，并按照插入顺序移除最早的条目（FIFO）。
    
    **Validates: Requirements 2.4, 2.5**
    """
    cache = DeduplicationCache(max_size=max_size)
    
    # 生成唯一的消息 ID
    message_ids = [f"msg_{i}" for i in range(num_messages)]
    
    # 添加所有消息
    for message_id in message_ids:
        cache.mark_processed(message_id)
    
    # 缓存应该只保留最新的 max_size 个消息
    # 最早的消息应该被移除
    oldest_messages = message_ids[:num_messages - max_size]
    newest_messages = message_ids[num_messages - max_size:]
    
    # 验证最早的消息已被移除
    for message_id in oldest_messages:
        assert not cache.is_processed(message_id), \
            f"Oldest message {message_id} should be removed from cache"
    
    # 验证最新的消息仍在缓存中
    for message_id in newest_messages:
        assert cache.is_processed(message_id), \
            f"Newest message {message_id} should still be in cache"


# Feature: feishu-ai-bot, Property 6: 缓存容量限制（FIFO 顺序）
# **Validates: Requirements 2.4, 2.5**
@settings(max_examples=100)
@given(
    batch_size=st.integers(min_value=10, max_value=50),
    num_batches=st.integers(min_value=3, max_value=10)
)
def test_cache_fifo_order(batch_size, num_batches):
    """
    Property 6: 缓存容量限制（FIFO 顺序）
    
    For any 分批添加的消息序列，当缓存容量超过限制时，
    应该按照 FIFO 顺序移除最早的条目。
    
    **Validates: Requirements 2.4, 2.5**
    """
    max_size = batch_size * 2  # 缓存容量为两批消息
    cache = DeduplicationCache(max_size=max_size)
    
    all_batches = []
    
    # 分批添加消息
    for batch_num in range(num_batches):
        batch = [f"batch{batch_num}_msg{i}" for i in range(batch_size)]
        all_batches.append(batch)
        
        for message_id in batch:
            cache.mark_processed(message_id)
    
    # 只有最后两批消息应该在缓存中
    # 计算应该保留的批次
    if num_batches <= 2:
        # 如果总批次数不超过2，所有消息都应该在缓存中
        for batch in all_batches:
            for message_id in batch:
                assert cache.is_processed(message_id), \
                    f"Message {message_id} should be in cache"
    else:
        # 最早的批次应该被移除
        removed_batches = all_batches[:num_batches - 2]
        for batch in removed_batches:
            for message_id in batch:
                assert not cache.is_processed(message_id), \
                    f"Old message {message_id} should be removed from cache"
        
        # 最后两批应该保留
        kept_batches = all_batches[num_batches - 2:]
        for batch in kept_batches:
            for message_id in batch:
                assert cache.is_processed(message_id), \
                    f"Recent message {message_id} should be in cache"


# Feature: feishu-ai-bot, Property 6: 缓存容量限制（边界情况）
# **Validates: Requirements 2.4, 2.5**
@settings(max_examples=100)
@given(max_size=st.integers(min_value=1, max_value=100))
def test_cache_capacity_at_boundary(max_size):
    """
    Property 6: 缓存容量限制（边界情况）
    
    For any max_size，当添加恰好 max_size 个消息时，所有消息都应该在缓存中；
    当添加 max_size + 1 个消息时，第一个消息应该被移除。
    
    **Validates: Requirements 2.4, 2.5**
    """
    cache = DeduplicationCache(max_size=max_size)
    
    # 添加恰好 max_size 个消息
    message_ids = [f"msg_{i}" for i in range(max_size)]
    for message_id in message_ids:
        cache.mark_processed(message_id)
    
    # 所有消息都应该在缓存中
    for message_id in message_ids:
        assert cache.is_processed(message_id), \
            f"Message {message_id} should be in cache at capacity"
    
    # 添加第 max_size + 1 个消息
    extra_message = f"msg_{max_size}"
    cache.mark_processed(extra_message)
    
    # 第一个消息应该被移除
    assert not cache.is_processed(message_ids[0]), \
        f"First message {message_ids[0]} should be removed after exceeding capacity"
    
    # 其他消息应该仍在缓存中
    for message_id in message_ids[1:]:
        assert cache.is_processed(message_id), \
            f"Message {message_id} should still be in cache"
    
    # 新消息应该在缓存中
    assert cache.is_processed(extra_message), \
        f"New message {extra_message} should be in cache"


# Feature: feishu-ai-bot, Property 6: 缓存容量限制（重复消息不影响容量）
# **Validates: Requirements 2.4, 2.5**
@settings(max_examples=100)
@given(
    unique_count=st.integers(min_value=5, max_value=20),
    repeat_count=st.integers(min_value=2, max_value=10)
)
def test_cache_capacity_with_duplicates(unique_count, repeat_count):
    """
    Property 6: 缓存容量限制（重复消息不影响容量）
    
    For any 包含重复消息的序列，重复标记同一消息不应该影响缓存容量，
    缓存应该只存储唯一的消息 ID。
    
    **Validates: Requirements 2.4, 2.5**
    """
    max_size = unique_count
    cache = DeduplicationCache(max_size=max_size)
    
    # 生成唯一消息 ID
    message_ids = [f"msg_{i}" for i in range(unique_count)]
    
    # 重复标记每个消息多次
    for _ in range(repeat_count):
        for message_id in message_ids:
            cache.mark_processed(message_id)
    
    # 所有唯一消息都应该在缓存中
    for message_id in message_ids:
        assert cache.is_processed(message_id), \
            f"Message {message_id} should be in cache after repeated marking"
    
    # 添加一个新消息，应该移除最早的消息
    new_message = f"msg_{unique_count}"
    cache.mark_processed(new_message)
    
    # 第一个消息应该被移除
    assert not cache.is_processed(message_ids[0]), \
        f"First message {message_ids[0]} should be removed"
    
    # 新消息应该在缓存中
    assert cache.is_processed(new_message), \
        f"New message {new_message} should be in cache"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
