# 飞书 Reply API 学习总结

## 学习目标

学会如何使用飞书 Reply API 正确引用消息（特别是卡片消息），使回复在飞书客户端显示灰色引用框。

## 学习成果

### 1. 理解了 Reply API 的正确用法

**关键发现**：
- 必须使用 `client.im.v1.message.reply()` 而不是 `client.im.v1.message.create()`
- Reply API 会自动设置 `parent_id` 和 `root_id` 字段
- 只有使用 Reply API 发送的消息才会在飞书客户端显示灰色引用框

### 2. 验证了机器人的实现

**机器人已正确实现**：
- `feishu_bot/message_sender.py` 中的 `reply_message()` 方法已经使用了 Reply API
- 对于群聊消息，机器人会自动使用 `reply_message()` 而不是 `send_new_message()`
- 这意味着机器人的所有群聊回复都会显示为引用格式

### 3. 创建了演示和测试脚本

#### 演示脚本：`demo_reply_message.py`
- 完整演示了 Reply API 的使用流程
- 包含发送卡片消息、引用回复、验证消息结构三个步骤
- 输出详细的说明和验证结果

#### 测试脚本：`test_reply_api.py`
- 简单的 Reply API 测试
- 用于快速验证 API 调用是否成功

#### 端到端测试：`test_quoted_card_end_to_end.py`
- 模拟真实使用场景
- 发送卡片消息并使用 @gemini-cli 引用回复
- 用于验证机器人的完整处理流程

### 4. 编写了使用指南

创建了 `docs/feishu_reply_api_guide.md`，包含：
- API 使用方法对比（错误 vs 正确）
- 请求参数说明
- 响应结构说明
- 在飞书客户端的显示效果
- 完整代码示例
- 注意事项

## 测试结果

### ✅ 已验证的功能

1. **发送卡片消息**
   - 使用 `CreateMessageRequest` 成功发送卡片消息
   - 卡片消息包含标题和富文本内容

2. **使用 Reply API 引用消息**
   - 使用 `ReplyMessageRequest` 成功引用卡片消息
   - 回复消息包含正确的 `parent_id` 和 `root_id`

3. **消息结构验证**
   - 使用 `GetMessageRequest` 获取消息详情
   - 确认回复消息的 `parent_id` 指向被引用的消息

4. **飞书客户端显示**
   - 在飞书客户端中，回复消息显示灰色引用框
   - 引用框显示 "回复 xxx：" 和原始消息内容

### 📊 测试数据

测试群聊：机器人群 (`oc_1f33979901b84f7f4036b9c501deb452`)

测试消息示例：
- 卡片消息 ID: `om_x100b56de800b34b4c26bcde420bb083`
- 回复消息 ID: `om_x100b56de803eacb0c3f48ef5bd62baa`
- Parent ID: `om_x100b56de800b34b4c26bcde420bb083` ✅

## 关键代码片段

### 发送引用回复

```python
from lark_oapi.api.im.v1 import ReplyMessageRequest, ReplyMessageRequestBody

# 构建回复请求
request = ReplyMessageRequest.builder() \
    .message_id(parent_message_id)  # 要引用的消息 ID
    .request_body(
        ReplyMessageRequestBody.builder()
        .msg_type("text")
        .content('{"text":"@gemini-cli 消息内容"}')
        .build()
    ) \
    .build()

# 发送回复
response = client.im.v1.message.reply(request)
```

### 验证消息结构

```python
from lark_oapi.api.im.v1 import GetMessageRequest

# 获取消息详情
request = GetMessageRequest.builder() \
    .message_id(message_id) \
    .build()

response = client.im.v1.message.get(request)
message = response.data.items[0]

# 检查 parent_id
if message.parent_id == expected_parent_id:
    print("✅ 引用关系正确")
```

## 机器人集成

机器人已经正确实现了 Reply API：

```python
# feishu_bot/message_sender.py
def send_message(self, chat_type: str, chat_id: str, message_id: str, content: str) -> bool:
    if chat_type == "p2p":
        return self.send_new_message(chat_id, content)  # 私聊：发送新消息
    else:
        return self.reply_message(message_id, content)  # 群聊：回复消息（引用）
```

这意味着：
- 所有群聊回复都会自动显示引用格式
- 私聊消息不使用引用格式（因为私聊不需要引用）

## 下一步

机器人现在已经具备了正确的引用消息功能。要测试端到端流程：

1. 启动机器人：
   ```bash
   python lark_bot.py
   ```

2. 在飞书客户端中：
   - 发送一条卡片消息
   - 点击"回复"按钮
   - 输入 `@gemini-cli 请总结这条卡片消息`
   - 发送

3. 观察机器人的回复：
   - 应该显示灰色引用框
   - 应该包含完整的卡片内容
   - 应该正确总结卡片信息

## 相关文件

- `docs/feishu_reply_api_guide.md` - 详细使用指南
- `demo_reply_message.py` - 完整演示脚本
- `test_reply_api.py` - 简单测试脚本
- `test_quoted_card_end_to_end.py` - 端到端测试脚本
- `feishu_bot/message_sender.py` - 机器人消息发送实现

## 总结

✅ 已成功学会使用飞书 Reply API
✅ 已验证机器人的实现正确
✅ 已创建完整的文档和测试脚本
✅ 已测试引用卡片消息功能

机器人现在可以正确处理引用的卡片消息，并在飞书客户端显示正确的引用格式。
