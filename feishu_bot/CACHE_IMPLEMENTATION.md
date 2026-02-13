# DeduplicationCache 实现文档

## 概述

`DeduplicationCache` 是飞书 AI 机器人的消息去重缓存组件，用于防止重复处理相同的消息。该组件使用 FIFO（先进先出）队列实现，自动移除最早的条目以保持固定的缓存容量。

## 设计原则

1. **FIFO 队列**: 使用 `collections.deque` 实现，自动移除最早的条目
2. **固定容量**: 默认最大容量为 1000 条消息 ID
3. **快速查找**: 使用 `set` 提供 O(1) 时间复杂度的查找
4. **简单易用**: 提供清晰的 API 接口

## 实现细节

### 数据结构

- **_cache**: `collections.deque` - 存储消息 ID 的双端队列，设置 `maxlen` 自动移除最早条目
- **_cache_set**: `Set[str]` - 用于快速查找的集合，提供 O(1) 查找性能
- **max_size**: `int` - 缓存的最大容量

### 核心方法

#### `__init__(max_size: int = 1000)`

初始化去重缓存。

**参数**:
- `max_size`: 缓存的最大容量，默认 1000

**示例**:
```python
cache = DeduplicationCache()  # 使用默认容量
cache = DeduplicationCache(max_size=500)  # 自定义容量
```

#### `is_processed(message_id: str) -> bool`

检查消息是否已处理。

**参数**:
- `message_id`: 消息的唯一标识符

**返回**:
- `True` 如果消息已经被处理过
- `False` 如果消息是新的

**时间复杂度**: O(1)

**示例**:
```python
if cache.is_processed("msg_001"):
    print("消息已处理，跳过")
else:
    print("新消息，开始处理")
```

#### `mark_processed(message_id: str) -> None`

标记消息为已处理。

**参数**:
- `message_id`: 消息的唯一标识符

**行为**:
- 如果消息已在缓存中，不会重复添加
- 如果缓存已满，自动移除最早的条目
- 同步更新 deque 和 set

**时间复杂度**: O(1)

**示例**:
```python
cache.mark_processed("msg_001")
```

## 使用场景

### 场景 1: 防止重复处理飞书消息

```python
from feishu_bot import DeduplicationCache

cache = DeduplicationCache()

def handle_message(message_id: str, content: str):
    # 检查消息是否已处理
    if cache.is_processed(message_id):
        logger.info(f"消息 {message_id} 已处理，跳过")
        return
    
    # 标记消息为已处理
    cache.mark_processed(message_id)
    
    # 处理消息
    process_message(content)
```

### 场景 2: 自定义缓存容量

```python
# 对于高流量场景，可以增加缓存容量
cache = DeduplicationCache(max_size=5000)

# 对于低流量场景，可以减少缓存容量
cache = DeduplicationCache(max_size=100)
```

### 场景 3: 测试和调试

```python
# 创建小容量缓存用于测试
cache = DeduplicationCache(max_size=5)

# 添加消息
for i in range(10):
    cache.mark_processed(f"msg_{i:03d}")

# 验证 FIFO 行为
assert not cache.is_processed("msg_000")  # 最早的被移除
assert cache.is_processed("msg_009")      # 最新的保留
```

## 性能特性

- **查找性能**: O(1) - 使用 set 进行快速查找
- **插入性能**: O(1) - deque 的 append 操作
- **空间复杂度**: O(n) - n 为 max_size
- **内存占用**: 约 8 bytes × max_size（64位系统）

## 线程安全

**注意**: 当前实现不是线程安全的。如果需要在多线程环境中使用，需要添加锁机制：

```python
import threading

class ThreadSafeDeduplicationCache(DeduplicationCache):
    def __init__(self, max_size: int = 1000):
        super().__init__(max_size)
        self._lock = threading.Lock()
    
    def is_processed(self, message_id: str) -> bool:
        with self._lock:
            return super().is_processed(message_id)
    
    def mark_processed(self, message_id: str) -> None:
        with self._lock:
            super().mark_processed(message_id)
```

## 测试覆盖

完整的单元测试位于 `tests/test_cache.py`，包括：

1. ✅ 新消息标记为未处理
2. ✅ 标记消息后返回已处理
3. ✅ 多个消息的处理
4. ✅ 重复标记同一消息
5. ✅ 缓存容量限制
6. ✅ FIFO 行为验证
7. ✅ 自定义最大容量
8. ✅ 空缓存处理
9. ✅ 不同类型的消息 ID

运行测试：
```bash
python -m pytest tests/test_cache.py -v
```

## 需求验证

该实现满足以下需求：

- ✅ **Requirement 2.1**: 检查消息 ID 是否已在缓存中
- ✅ **Requirement 2.2**: 跳过已处理的消息
- ✅ **Requirement 2.3**: 添加新消息 ID 到缓存
- ✅ **Requirement 2.4**: 缓存大小超过 1000 时自动移除最早条目
- ✅ **Requirement 2.5**: 按插入顺序维护消息 ID

## 未来改进

1. **持久化**: 支持将缓存持久化到磁盘，以便重启后恢复
2. **过期策略**: 支持基于时间的过期策略（TTL）
3. **统计信息**: 添加缓存命中率、大小等统计信息
4. **分布式支持**: 支持 Redis 等分布式缓存后端

## 参考资料

- [Python collections.deque 文档](https://docs.python.org/3/library/collections.html#collections.deque)
- [飞书 AI 机器人设计文档](../.kiro/specs/feishu-ai-bot/design.md)
- [需求文档](../.kiro/specs/feishu-ai-bot/requirements.md)
