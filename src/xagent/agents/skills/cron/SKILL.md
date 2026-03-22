---
name: cron
description: 通过 HTTP API 管理定时任务 - 创建、查询、暂停、恢复、删除任务
metadata: { "xagent": { "emoji": "⏰" } }
---

# 定时任务管理

使用 `call_cron_api` tool 通过 HTTP API 管理定时任务。

**关键要求**: 
- 所有 cron 操作都通过 `call_cron_api` tool 调用 Web Admin 的 API 端点
- 确保 Web Admin 服务运行在 `http://localhost:8080`

## 常用操作

使用 `call_cron_api` tool 执行以下操作：

```python
# 列出所有任务
call_cron_api(action="list")

# 查看任务详情（包含状态信息）
call_cron_api(action="get", job_id="<job_id>")

# 删除任务
call_cron_api(action="delete", job_id="<job_id>")

# 暂停/恢复任务
call_cron_api(action="pause", job_id="<job_id>")
call_cron_api(action="resume", job_id="<job_id>")

# 立即执行一次
call_cron_api(action="run", job_id="<job_id>")
```

## 创建任务

支持两种任务类型：
- **text**：定时向频道发送固定消息（内容固定不变）
- **agent**：定时向 Agent 提问并发送回复到频道（内容动态生成）

### 任务类型判断指南

根据用户需求判断应该创建哪种类型的任务：

**创建 text 任务的情况：**
- 发送固定不变的提醒消息（如"该喝水了！"、"该休息了！"）
- 发送固定的通知内容（如"会议即将开始"）
- 发送预设的问候语（如"早上好！"）

**创建 agent 任务的情况：**
- 需要动态生成内容（如"报时"需要生成当前时间）
- 需要查询信息（如"今天有什么待办事项？"、"查询今日天气"）
- 需要 AI 处理或分析（如"总结一下今天的消息"）
- 内容会根据时间、上下文变化（如"距离截止日期还有几天？"）

**判断口诀：**
- 如果消息内容是**固定不变**的 → 用 **text** 类型
- 如果消息内容需要**动态生成**或**查询** → 用 **agent** 类型

### 快速创建

使用 `call_cron_api` tool 创建任务：

**重要**：创建任务前，必须从用户获取或使用以下真实值：
- `id`: 任务唯一标识符（使用有意义的名称，如 "drink-water-reminder"）
- `target_user`: 用户 ID（从环境变量 FEISHU_USER_ID 获取，当前值：155529283）
- `target_chat`: 聊天 ID（从环境变量 FEISHU_CHAT_ID 获取，当前值：oc_585f29d10679c7a0b5c3bf0d34adba90）

```python
# 每天 9:00 发送固定文本消息（text 类型 - 内容固定不变）
call_cron_api(
    action="create",
    job_spec="""{
        "id": "daily-morning-greeting",
        "type": "text",
        "name": "每日早安",
        "cron": "0 9 * * *",
        "channel": "feishu",
        "target_user": "155529283",
        "target_chat": "oc_585f29d10679c7a0b5c3bf0d34adba90",
        "text": "早上好！"
    }"""
)

# 每小时报时（agent 类型 - 需要动态生成当前时间）
call_cron_api(
    action="create",
    job_spec="""{
        "id": "hourly-chime",
        "type": "agent",
        "name": "整点报时",
        "cron": "0 * * * *",
        "channel": "feishu",
        "target_user": "155529283",
        "target_chat": "oc_585f29d10679c7a0b5c3bf0d34adba90",
        "text": "现在几点了？请报时。"
    }"""
)

# 每 2 小时查询待办事项（agent 类型 - 需要查询信息）
call_cron_api(
    action="create",
    job_spec="""{
        "id": "check-todos-2h",
        "type": "agent",
        "name": "检查待办",
        "cron": "0 */2 * * *",
        "channel": "feishu",
        "target_user": "155529283",
        "target_chat": "oc_585f29d10679c7a0b5c3bf0d34adba90",
        "text": "我有什么待办事项？"
    }"""
)
```

### 必填参数

创建任务需要在 `job_spec` JSON 中提供：
- `id`：任务唯一标识符（使用有意义的名称，如 "drink-water-reminder"）
- `type`：任务类型（text 或 agent）
- `name`：任务名称
- `cron`：cron 表达式（如 `"0 9 * * *"` 表示每天 9:00）
- `channel`：目标频道（feishu / console）
- `target_user`：用户 ID（可选，当 target_chat 为空时使用）
- `target_chat`：聊天 ID（优先使用，私聊或群聊都可以）
- `text`：消息内容（text 类型）或提问内容（agent 类型）

### 使用 JSON 创建（复杂配置）

```python
# 准备完整的 job spec JSON
job_spec = """{
    "id": "workday-reminder",
    "type": "agent",
    "name": "工作日提醒",
    "cron": "30 8 * * 1-5",
    "channel": "feishu",
    "target_user": "155529283",
    "target_chat": "oc_585f29d10679c7a0b5c3bf0d34adba90",
    "text": "今天有什么重要任务？",
    "enabled": true
}"""

call_cron_api(action="create", job_spec=job_spec)
```

## Cron 表达式示例

```
0 9 * * *      # 每天 9:00
0 */2 * * *    # 每 2 小时
30 8 * * 1-5   # 工作日 8:30
0 0 * * 0      # 每周日零点
*/15 * * * *   # 每 15 分钟
```

## 使用建议

- **执行操作时**: 使用 `call_cron_api` tool，无需指定工作目录或路径
- **创建任务前**: 先询问用户所有必填参数（id, type, name, cron, channel, target_chat 或 target_user, text），确认无误后一次性创建
- **任务类型选择**: 
  - 仔细分析用户需求，判断是发送固定消息还是需要动态生成内容
  - 涉及"报时"、"查询"、"总结"等动态内容 → 必须使用 **agent** 类型
  - 简单的提醒、通知 → 使用 **text** 类型
- **任务 ID 命名**: 使用有意义的英文名称，用连字符分隔，如 "drink-water-reminder", "daily-report"
- **避免重复创建**: 创建任务前，先用 `call_cron_api(action="list")` 检查是否已存在同名任务
- 暂停/删除/恢复前，用 `call_cron_api(action="list")` 查找 job_id
- 查看任务状态时，用 `call_cron_api(action="get", job_id="<job_id>")` 获取完整信息（包含 spec 和 state）
- 确保 Web Admin 服务运行在 `http://localhost:8080`
- 所有操作通过 HTTP API 执行，不依赖特定的文件系统路径
