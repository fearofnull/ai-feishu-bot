# Bug修复：/help 命令路由问题

## 问题描述

用户报告 `/help` 命令被路由到 Claude AI，而不是作为会话命令被处理。

## 根本原因

在 `feishu_bot/feishu_bot.py` 中，`_handle_session_command` 方法使用了硬编码的命令列表，只包含：
- `/new` 或 `新会话`
- `/session` 或 `会话信息`
- `/history` 或 `历史记录`

而 `/help` 命令虽然在 `SessionManager` 中已经实现，但没有在 `feishu_bot.py` 的硬编码列表中，导致该命令通过了会话命令检查，被路由到 AI。

## 问题分析

### 原有实现的问题

1. **重复的命令定义**：
   - `SessionManager` 中定义了完整的命令列表（包括 `/help`）
   - `FeishuBot._handle_session_command` 中又硬编码了部分命令
   - 两处定义不一致，导致维护困难

2. **命令处理流程**：
   ```
   用户消息 → 命令解析 → _handle_session_command (硬编码检查)
                                    ↓
                              未匹配 /help
                                    ↓
                              路由到 AI ❌
   ```

## 解决方案

### 修改内容

统一使用 `SessionManager` 处理所有会话命令：

```python
def _handle_session_command(
    self,
    user_id: str,
    message: str,
    chat_type: str,
    chat_id: str,
    message_id: str
) -> bool:
    """处理会话命令"""
    # 检查是否为会话命令
    if not self.session_manager.is_session_command(message):
        return False
    
    # 使用 session_manager 处理命令
    response = self.session_manager.handle_session_command(user_id, message)
    
    # 如果是新会话命令，额外清除 CLI 会话
    message_lower = message.lower().strip()
    if message_lower in [cmd.lower() for cmd in self.session_manager.NEW_SESSION_COMMANDS]:
        for provider in ["claude", "gemini"]:
            try:
                cli_executor = self.executor_registry.get_executor(provider, "cli")
                if hasattr(cli_executor, 'clear_session'):
                    cli_executor.clear_session(user_id)
            except:
                pass
    
    # 发送响应
    if response:
        self.message_sender.send_message(
            chat_type, chat_id, message_id, response
        )
        return True
    
    return False
```

### 修改后的流程

```
用户消息 → 命令解析 → _handle_session_command
                              ↓
                    session_manager.is_session_command()
                              ↓
                         匹配 /help ✅
                              ↓
                    session_manager.handle_session_command()
                              ↓
                         返回帮助信息
```

## 优势

1. **单一数据源**：所有会话命令定义在 `SessionManager` 中
2. **易于维护**：添加新命令只需修改 `SessionManager`
3. **一致性**：所有会话命令使用相同的处理逻辑
4. **可扩展**：未来添加新命令无需修改 `FeishuBot`

## 测试验证

创建了 `test_scripts/test_help_command_routing.py` 测试脚本，包含4个测试：

1. ✅ 会话命令检测：验证所有会话命令都能被正确识别
2. ✅ 命令解析与 help：验证命令解析不影响会话命令识别
3. ✅ help 命令响应：验证 help 命令返回正确的帮助信息
4. ✅ 消息流程模拟：模拟完整的消息处理流程

所有测试通过 ✅

## 影响范围

- **修改文件**：
  - `feishu_bot/feishu_bot.py`：重构 `_handle_session_command` 方法
  - `README.md`：添加 v1.0.1 版本说明
  - `test_scripts/test_help_command_routing.py`：新增测试脚本

- **影响功能**：
  - 所有会话命令（`/new`, `/session`, `/history`, `/help`）
  - 命令路由逻辑

- **向后兼容**：完全兼容，用户体验无变化

## 部署说明

1. 拉取最新代码：`git pull`
2. 无需重新安装依赖
3. 重启机器人服务即可生效

## 相关文档

- [用户指南](USER_GUIDE.md)：包含所有可用命令说明
- [配置指南](CONFIGURATION.md)：机器人配置说明
- [测试指南](INTEGRATION_TESTING_GUIDE.md)：集成测试说明

## 版本信息

- **修复版本**：v1.0.1
- **修复日期**：2025-02-25
- **提交哈希**：37a3089
