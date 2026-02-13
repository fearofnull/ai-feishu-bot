"""
DeduplicationCache 使用示例
演示消息去重缓存的基本用法
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from feishu_bot import DeduplicationCache


def main():
    print("=" * 60)
    print("DeduplicationCache 使用示例")
    print("=" * 60)
    
    # 创建缓存实例
    cache = DeduplicationCache(max_size=5)
    print("\n✅ 创建缓存实例（最大容量: 5）\n")
    
    # 示例 1: 检查新消息
    print("示例 1: 检查新消息")
    print("-" * 40)
    message_id = "msg_001"
    is_processed = cache.is_processed(message_id)
    print(f"消息 '{message_id}' 是否已处理: {is_processed}")
    print()
    
    # 示例 2: 标记消息为已处理
    print("示例 2: 标记消息为已处理")
    print("-" * 40)
    cache.mark_processed(message_id)
    is_processed = cache.is_processed(message_id)
    print(f"标记后，消息 '{message_id}' 是否已处理: {is_processed}")
    print()
    
    # 示例 3: 处理多个消息
    print("示例 3: 处理多个消息")
    print("-" * 40)
    messages = ["msg_002", "msg_003", "msg_004", "msg_005"]
    for msg_id in messages:
        cache.mark_processed(msg_id)
        print(f"✓ 标记消息 '{msg_id}' 为已处理")
    print()
    
    # 示例 4: 缓存容量限制（FIFO）
    print("示例 4: 缓存容量限制（FIFO）")
    print("-" * 40)
    print("当前缓存已满（5条消息），添加新消息...")
    cache.mark_processed("msg_006")
    print(f"✓ 添加消息 'msg_006'")
    print()
    
    # 检查最早的消息是否被移除
    print("检查消息状态:")
    print(f"  msg_001 (最早): {cache.is_processed('msg_001')} ❌ (已被移除)")
    print(f"  msg_002: {cache.is_processed('msg_002')} ✓")
    print(f"  msg_003: {cache.is_processed('msg_003')} ✓")
    print(f"  msg_004: {cache.is_processed('msg_004')} ✓")
    print(f"  msg_005: {cache.is_processed('msg_005')} ✓")
    print(f"  msg_006 (最新): {cache.is_processed('msg_006')} ✓")
    print()
    
    # 示例 5: 重复标记
    print("示例 5: 重复标记同一消息")
    print("-" * 40)
    cache.mark_processed("msg_002")  # 重复标记
    print(f"重复标记 'msg_002'，仍然在缓存中: {cache.is_processed('msg_002')}")
    print()
    
    print("=" * 60)
    print("✅ 演示完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
