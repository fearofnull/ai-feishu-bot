"""
消息去重缓存单元测试
"""
import pytest
from feishu_bot.cache import DeduplicationCache


class TestDeduplicationCache:
    """DeduplicationCache 单元测试"""
    
    def test_new_message_not_processed(self):
        """测试新消息标记为未处理"""
        cache = DeduplicationCache()
        message_id = "msg_001"
        
        assert not cache.is_processed(message_id)
    
    def test_mark_processed_makes_message_processed(self):
        """测试标记消息后返回已处理"""
        cache = DeduplicationCache()
        message_id = "msg_001"
        
        cache.mark_processed(message_id)
        
        assert cache.is_processed(message_id)
    
    def test_multiple_messages(self):
        """测试多个消息的处理"""
        cache = DeduplicationCache()
        
        cache.mark_processed("msg_001")
        cache.mark_processed("msg_002")
        cache.mark_processed("msg_003")
        
        assert cache.is_processed("msg_001")
        assert cache.is_processed("msg_002")
        assert cache.is_processed("msg_003")
        assert not cache.is_processed("msg_004")
    
    def test_duplicate_mark_processed(self):
        """测试重复标记同一消息"""
        cache = DeduplicationCache()
        message_id = "msg_001"
        
        cache.mark_processed(message_id)
        cache.mark_processed(message_id)  # 重复标记
        
        assert cache.is_processed(message_id)
    
    def test_cache_capacity_limit(self):
        """测试缓存容量限制（1000条）"""
        cache = DeduplicationCache(max_size=10)
        
        # 添加 15 条消息
        for i in range(15):
            cache.mark_processed(f"msg_{i:03d}")
        
        # 最早的 5 条应该被移除
        assert not cache.is_processed("msg_000")
        assert not cache.is_processed("msg_001")
        assert not cache.is_processed("msg_002")
        assert not cache.is_processed("msg_003")
        assert not cache.is_processed("msg_004")
        
        # 最新的 10 条应该还在
        assert cache.is_processed("msg_005")
        assert cache.is_processed("msg_014")
    
    def test_fifo_behavior(self):
        """测试 FIFO 行为"""
        cache = DeduplicationCache(max_size=3)
        
        cache.mark_processed("msg_001")
        cache.mark_processed("msg_002")
        cache.mark_processed("msg_003")
        
        # 缓存已满，添加新消息应该移除最早的
        cache.mark_processed("msg_004")
        
        assert not cache.is_processed("msg_001")  # 最早的被移除
        assert cache.is_processed("msg_002")
        assert cache.is_processed("msg_003")
        assert cache.is_processed("msg_004")
    
    def test_custom_max_size(self):
        """测试自定义最大容量"""
        cache = DeduplicationCache(max_size=5)
        
        for i in range(10):
            cache.mark_processed(f"msg_{i:03d}")
        
        # 只保留最新的 5 条
        assert not cache.is_processed("msg_000")
        assert not cache.is_processed("msg_004")
        assert cache.is_processed("msg_005")
        assert cache.is_processed("msg_009")
    
    def test_empty_cache(self):
        """测试空缓存"""
        cache = DeduplicationCache()
        
        assert not cache.is_processed("any_message")
    
    def test_message_id_types(self):
        """测试不同类型的消息 ID"""
        cache = DeduplicationCache()
        
        # 测试不同格式的消息 ID
        ids = [
            "msg_001",
            "om_1234567890abcdef",
            "message-with-dashes",
            "message_with_underscores",
            "123456789",
        ]
        
        for msg_id in ids:
            cache.mark_processed(msg_id)
        
        for msg_id in ids:
            assert cache.is_processed(msg_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
