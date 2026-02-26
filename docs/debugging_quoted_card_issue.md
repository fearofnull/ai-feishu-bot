# 调试引用卡片消息问题

## 问题描述

机器人报告错误："处理消息时发生错误：不支持的消息类型: interactive。请发送文本消息。"

这个错误来自 `message_handler.py` 的 `parse_message_content()` 方法，当 `message_type != "text"` 时抛出。

## 预期行为

当用户引用卡片消息并发送文本消息时：
1. WebSocket 事件中的 `data.event.message.message_type` 应该是 `"text"`（当前消息是文本）
2. `data.event.message.parent_id` 应该指向被引用的卡片消息
3. 机器人应该：
   - 解析当前文本消息（包含 "@gemini-cli" 等）
   - 使用 `parent_id` 获取被引用的卡片消息
   - 提取卡片内容
   - 组合两条消息发送给 AI

## 实际行为

机器人报告 `message_type` 是 `"interactive"`，这意味着：
- 要么 WebSocket 事件结构与预期不同
- 要么用户发送的不是文本消息而是卡片消息

## 可能的原因

### 原因 1: 飞书 API 行为变化

飞书 API 可能在 WebSocket 事件中返回不同的消息结构。当消息引用另一条消息时，可能：
- 将被引用消息的类型作为当前消息的类型
- 或者在事件中包含被引用消息的完整内容

### 原因 2: 测试方法问题

使用 MCP 工具发送的消息是以应用身份（tenant_access_token）发送的，不是以用户身份发送的。机器人可能：
- 不响应自己发送的消息
- 或者对应用发送的消息有不同的处理逻辑

### 原因 3: 消息发送方式问题

可能用户在飞书客户端中的操作方式导致发送的不是文本消息：
- 直接转发卡片消息（而不是引用+文本）
- 使用了某种特殊的引用方式

## 调试步骤

### 步骤 1: 添加详细日志

已在 `feishu_bot.py` 第 251-254 行添加调试日志：
```python
logger.info(f"Message type: {data.event.message.message_type}")
if hasattr(data.event.message, 'parent_id'):
    logger.info(f"Parent ID: {data.event.message.parent_id}")
```

### 步骤 2: 手动测试

需要用户在飞书客户端中手动测试：

1. 找到机器人发送的卡片消息
2. 点击"引用"按钮
3. 输入文本消息（如 "@gemini-cli 这个错误怎么解决？"）
4. 发送消息
5. 查看机器人日志中的 `Message type` 和 `Parent ID`

### 步骤 3: 检查 WebSocket 事件结构

如果日志显示 `message_type` 确实是 `"interactive"`，需要：

1. 运行 `debug_websocket_event.py` 脚本查看完整事件结构
2. 检查飞书 API 文档确认 WebSocket 事件格式
3. 可能需要调整代码以适应实际的事件结构

## 解决方案

### 方案 1: 修改 parse_message_content 处理引用消息

如果 WebSocket 事件中的 `message_type` 确实是被引用消息的类型，需要修改代码：

```python
def parse_message_content(self, message) -> str:
    # 检查是否是引用消息
    if hasattr(message, 'parent_id') and message.parent_id:
        # 引用消息：当前消息可能是任何类型，需要特殊处理
        # 尝试提取当前消息的文本内容
        if hasattr(message, 'content'):
            try:
                content = json.loads(message.content)
                # 尝试提取 text 字段
                if 'text' in content:
                    return self._clean_mentions(content['text'])
            except:
                pass
        # 如果无法提取文本，返回空字符串
        return ""
    
    # 非引用消息：按原逻辑处理
    if message_type != "text":
        raise ValueError(f"不支持的消息类型: {message_type}")
    # ... 原有逻辑
```

### 方案 2: 在 feishu_bot.py 中提前处理

在调用 `parse_message_content` 之前检查是否是引用消息：

```python
# 检查是否是引用消息
if hasattr(data.event.message, 'parent_id') and data.event.message.parent_id:
    # 引用消息：直接提取 content 中的 text 字段
    try:
        content = json.loads(data.event.message.content)
        message_content = content.get('text', '')
        if message_content:
            message_content = self.message_handler._clean_mentions(message_content)
    except:
        message_content = ""
else:
    # 非引用消息：使用原有逻辑
    message_content = self.message_handler.parse_message_content(
        data.event.message
    )
```

## 下一步

1. 等待用户手动测试并提供日志输出
2. 根据日志确定实际的 WebSocket 事件结构
3. 选择合适的解决方案并实现
4. 测试修复是否有效
