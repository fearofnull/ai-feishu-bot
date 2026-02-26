# 飞书 Reply API 使用指南

## 概述

飞书 Reply API 用于创建引用消息（带灰色引用框的回复）。这是实现消息引用功能的正确方式。

## 关键区别

### ❌ 错误方式：使用 Create Message API
```python
# 这种方式只会发送普通消息，不会显示引用框
request = CreateMessageRequest.builder() \
    .receive_id_type("chat_id") \
    .request_body(
        CreateMessageRequestBody.builder()
        .receive_id(chat_id)
        .msg_type("text")
        .content('{"text":"@gemini-cli 消息内容"}')
        .build()
    ) \
    .build()

response = client.im.v1.message.create(request)
```

### ✅ 正确方式：使用 Reply Message API
```python
# 这种方式会创建引用消息，显示灰色引用框
request = ReplyMessageRequest.builder() \
    .message_id(parent_message_id)  # 要引用的消息 ID
    .request_body(
        ReplyMessageRequestBody.builder()
        .msg_type("text")
        .content('{"text":"@gemini-cli 消息内容"}')
        .build()
    ) \
    .build()

response = client.im.v1.message.reply(request)
```

## API 端点

```
POST /open-apis/im/v1/messages/:message_id/reply
```

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message_id | string | 是 | 要引用的消息 ID（路径参数） |
| msg_type | string | 是 | 消息类型（text, interactive 等） |
| content | string | 是 | 消息内容（JSON 字符串） |

## 响应结构

成功的回复消息会包含以下字段：

```json
{
  "message_id": "om_xxx",      // 新消息的 ID
  "parent_id": "om_yyy",       // 被引用消息的 ID
  "root_id": "om_yyy",         // 引用链的根消息 ID
  "create_time": "1772006461996",
  "msg_type": "text",
  "body": {
    "content": "{\"text\":\"消息内容\"}"
  }
}
```

## 在飞书客户端的显示效果

使用 Reply API 发送的消息会在飞书客户端显示为：

```
┌─────────────────────────────┐
│ 回复 用户名：               │  ← 灰色引用框
│ 原始消息内容...             │
└─────────────────────────────┘
你的回复内容
```

## 完整示例

参考 `demo_reply_message.py` 文件，该脚本演示了：

1. 发送一条卡片消息
2. 使用 Reply API 引用该卡片消息
3. 验证回复消息包含正确的 parent_id

运行示例：
```bash
python demo_reply_message.py
```

## 在机器人中的应用

在 `feishu_bot/message_sender.py` 中，机器人已经正确实现了 Reply API：

```python
def reply_message(self, message_id: str, content: str) -> bool:
    """回复消息（用于群聊）"""
    try:
        request = ReplyMessageRequest.builder() \
            .message_id(message_id) \
            .request_body(
                ReplyMessageRequestBody.builder()
                .msg_type("text")
                .content(f'{{"text":"{self._escape_json(content)}"}}')
                .build()
            ) \
            .build()
        
        response = self.client.im.v1.message.reply(request)
        
        if not response.success():
            logger.error(f"Failed to reply message: {response.msg}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error replying message: {e}")
        return False
```

## 测试结果

✅ 已验证功能：
- 发送卡片消息
- 使用 Reply API 引用卡片消息
- 回复消息包含正确的 parent_id 和 root_id
- 在飞书客户端显示灰色引用框

## 注意事项

1. **必须使用 Reply API**：只有使用 `client.im.v1.message.reply()` 才能创建引用消息
2. **message_id 参数**：传入要引用的消息 ID，不是 chat_id
3. **自动设置 parent_id**：Reply API 会自动设置 parent_id 和 root_id
4. **支持所有消息类型**：可以引用文本消息、卡片消息等任何类型的消息

## 相关文件

- `feishu_bot/message_sender.py` - 消息发送器实现
- `demo_reply_message.py` - 完整演示脚本
- `test_reply_api.py` - 简单测试脚本
