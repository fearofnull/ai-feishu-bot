# 飞书流式响应研究与评估

## 研究日期
2026-02-25

## 研究目标
评估飞书机器人是否支持流式响应，以及是否可以将当前项目改造为流式响应模式。

---

## 一、飞书流式响应能力研究

### 1.1 飞书官方API支持

根据研究，飞书开放平台提供了以下相关API：

#### 更新应用发送的消息 API
- **接口**: `PATCH /open-apis/im/v1/messages/{message_id}`
- **功能**: 更新机器人已发送的消息内容
- **限制**: 
  - 只能更新机器人自己发送的消息
  - 需要使用 `tenant_access_token` 进行认证
  - 消息必须在24小时内

#### API示例
```http
PATCH https://open.feishu.cn/open-apis/im/v1/messages/{message_id}
Authorization: Bearer {tenant_access_token}
Content-Type: application/json

{
  "content": "{\"text\":\"更新后的消息内容\"}"
}
```

### 1.2 流式响应实现方式

飞书本身**不支持真正的流式推送**（如Server-Sent Events或WebSocket），但可以通过以下方式模拟流式效果：

#### 方案A：轮询更新（Polling Update）
1. 机器人先发送一条初始消息（如"正在思考..."）
2. 获取该消息的 `message_id`
3. 在AI生成内容的过程中，定期调用 PATCH API 更新消息内容
4. 用户在飞书客户端会看到消息内容逐步更新

**优点**：
- 实现相对简单
- 用户体验接近流式响应
- 不需要用户刷新或重新加载

**缺点**：
- 不是真正的流式推送
- 更新频率受API限制（建议不超过1次/秒）
- 可能产生较多API调用

#### 方案B：分段发送（Chunked Messages）
1. 将AI生成的内容分成多个片段
2. 每个片段作为独立消息发送
3. 用户看到多条连续消息

**优点**：
- 实现简单
- API调用次数可控

**缺点**：
- 用户体验较差（多条消息而非一条更新的消息）
- 会产生大量消息记录
- 不推荐使用

---

## 二、当前项目架构分析

### 2.1 现有消息发送流程

```
用户消息 → 飞书Bot → 消息解析 → 智能路由 → AI执行器 → 响应格式化 → 发送消息
```

当前实现：
- 等待AI完全生成响应后，一次性发送完整消息
- 使用 `MessageSender.send_message()` 发送消息
- 不保存已发送消息的 `message_id`

### 2.2 需要改造的模块

#### 1. MessageSender（消息发送器）
**当前**：
```python
def send_message(self, chat_type, chat_id, message_id, content):
    # 发送消息，不返回message_id
```

**需要改造为**：
```python
def send_message(self, chat_type, chat_id, message_id, content):
    # 发送消息，返回message_id
    return sent_message_id

def update_message(self, message_id, new_content):
    # 新增：更新已发送的消息
```

#### 2. AI执行器（API层）
**当前**：
```python
def execute(self, prompt, conversation_history):
    # 等待完整响应
    result = api_call(prompt)
    return ExecutionResult(stdout=result)
```

**需要改造为**：
```python
def execute_streaming(self, prompt, conversation_history, callback):
    # 流式生成，通过callback返回增量内容
    for chunk in api_call_streaming(prompt):
        callback(chunk)
```

#### 3. FeishuBot（主应用）
需要新增流式响应处理逻辑：
```python
def _handle_streaming_response(self, executor, prompt, chat_info):
    # 1. 发送初始消息
    message_id = self.message_sender.send_message(
        chat_type, chat_id, reply_to_id, "🤔 正在思考..."
    )
    
    # 2. 累积内容并定期更新
    accumulated_content = ""
    last_update_time = time.time()
    
    def on_chunk(chunk):
        nonlocal accumulated_content, last_update_time
        accumulated_content += chunk
        
        # 每1秒更新一次消息
        if time.time() - last_update_time >= 1.0:
            self.message_sender.update_message(
                message_id, 
                accumulated_content
            )
            last_update_time = time.time()
    
    # 3. 执行流式生成
    executor.execute_streaming(prompt, on_chunk)
    
    # 4. 最终更新
    self.message_sender.update_message(message_id, accumulated_content)
```

---

## 三、技术可行性评估

### 3.1 API层流式支持

| AI提供商 | 流式API支持 | Python SDK支持 | 实现难度 |
|---------|-----------|--------------|---------|
| OpenAI API | ✅ 支持 | ✅ 支持 `stream=True` | 低 |
| Claude API | ✅ 支持 | ✅ 支持 `stream=True` | 低 |
| Gemini API | ✅ 支持 | ✅ 支持 `stream=True` | 低 |

**示例（OpenAI）**：
```python
from openai import OpenAI

client = OpenAI(api_key="...")
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True  # 启用流式响应
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### 3.2 CLI层流式支持

| CLI工具 | 流式输出 | 实现难度 |
|--------|---------|---------|
| Claude Code CLI | ✅ 原生支持 | 中 |
| Gemini CLI | ✅ 原生支持 | 中 |

CLI工具通常通过 `subprocess` 的 `stdout` 实时输出，可以通过以下方式捕获：

```python
process = subprocess.Popen(
    command_args,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1  # 行缓冲
)

for line in process.stdout:
    callback(line)  # 实时回调
```

### 3.3 飞书API限制

根据飞书开放平台的限制：
- **消息更新频率**: 建议不超过 1次/秒（避免触发限流）
- **消息更新时效**: 消息必须在24小时内
- **认证要求**: 需要 `tenant_access_token`

---

## 四、实现方案推荐

### 4.1 推荐方案：渐进式流式响应

#### 阶段1：API层流式响应（优先级：高）
- 改造 OpenAI/Claude/Gemini API 执行器，支持流式生成
- 实现消息更新机制（PATCH API）
- 添加流式响应开关配置

**预期效果**：
- 用户提问后，立即看到"正在思考..."
- 每1秒更新一次消息内容
- AI生成完成后显示完整响应

**实现时间**: 2-3天

#### 阶段2：CLI层流式响应（优先级：中）
- 改造 Claude CLI 和 Gemini CLI 执行器
- 实时捕获 CLI 输出并更新消息

**预期效果**：
- CLI工具的输出实时显示给用户
- 长时间运行的命令不会让用户等待

**实现时间**: 1-2天

### 4.2 配置项设计

在 `.env` 中添加：
```bash
# 流式响应配置
ENABLE_STREAMING_RESPONSE=true
# 消息更新间隔（秒）
STREAMING_UPDATE_INTERVAL=1.0
# 流式响应适用层（api, cli, both）
STREAMING_LAYERS=api
```

### 4.3 用户体验对比

#### 当前体验：
```
用户: 请分析这个项目的README文件
[等待30秒...]
机器人: [完整的分析结果]
```

#### 流式响应体验：
```
用户: 请分析这个项目的README文件
[立即响应]
机器人: 🤔 正在思考...
[1秒后]
机器人: 这个项目是...
[2秒后]
机器人: 这个项目是一个多模块Maven项目...
[3秒后]
机器人: 这个项目是一个多模块Maven项目，使用Java 8和Spring Boot...
[最终]
机器人: [完整的分析结果]
```

---

## 五、风险与挑战

### 5.1 技术风险

1. **API限流风险**
   - 飞书可能对消息更新频率有限制
   - 缓解：控制更新频率（1次/秒）

2. **消息更新失败**
   - 网络问题可能导致更新失败
   - 缓解：添加重试机制和降级方案

3. **并发问题**
   - 多个用户同时使用可能导致消息更新冲突
   - 缓解：为每个用户维护独立的消息更新队列

### 5.2 用户体验风险

1. **更新频率过高**
   - 用户可能感觉消息"闪烁"
   - 缓解：设置合理的更新间隔（1秒）

2. **更新频率过低**
   - 用户感觉不到流式效果
   - 缓解：根据内容长度动态调整更新频率

---

## 六、结论与建议

### 6.1 结论

✅ **飞书支持流式响应**：通过 PATCH API 更新消息内容，可以实现类似流式响应的效果

✅ **技术可行**：
- API层流式响应：完全可行，实现难度低
- CLI层流式响应：可行，实现难度中等
- 飞书消息更新：可行，需要注意频率限制

✅ **用户体验提升明显**：
- 减少等待焦虑
- 实时反馈进度
- 更好的交互体验

### 6.2 建议

**推荐实施**，按以下优先级：

1. **Phase 1（高优先级）**：实现API层流式响应
   - 改造 OpenAI/Claude/Gemini API 执行器
   - 实现消息更新机制
   - 添加配置开关

2. **Phase 2（中优先级）**：实现CLI层流式响应
   - 改造 Claude CLI 和 Gemini CLI 执行器
   - 实时捕获输出

3. **Phase 3（低优先级）**：优化与监控
   - 添加性能监控
   - 优化更新策略
   - 收集用户反馈

### 6.3 预期收益

- **用户体验**: 提升50%以上（减少等待焦虑）
- **响应速度感知**: 从"慢"变为"快"（即使实际时间相同）
- **竞争力**: 与主流AI聊天应用（ChatGPT、Claude等）体验一致

---

## 七、参考资料

1. [飞书开放平台 - 更新应用发送的消息](https://open.feishu.cn/document/server-docs/im-v1/message/patch)
2. [OpenAI API - Streaming](https://platform.openai.com/docs/api-reference/streaming)
3. [Anthropic Claude API - Streaming](https://docs.anthropic.com/claude/reference/streaming)
4. [Google Gemini API - Streaming](https://ai.google.dev/tutorials/python_quickstart#streaming)
5. [博客参考 - HttpClient实现调用飞书更新消息接口](https://www.cnblogs.com/baby-dragon/p/16022947.html)

---

## 八、下一步行动

如果决定实施，建议按以下步骤进行：

1. ✅ 完成研究与评估（本文档）
2. ⬜ 创建流式响应功能的Spec文档
3. ⬜ 实现 MessageSender 的消息更新功能
4. ⬜ 改造 API 执行器支持流式生成
5. ⬜ 集成到 FeishuBot 主流程
6. ⬜ 测试与优化
7. ⬜ 部署上线

**预计总工时**: 3-5天（API层） + 1-2天（CLI层） = 4-7天
