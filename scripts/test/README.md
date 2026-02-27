# 测试脚本目录

本目录包含用于测试飞书AI机器人的实用脚本。

## 脚本说明

### 集成测试
- `run_integration_test.py` - 主集成测试脚本，用于端到端测试机器人功能

### 消息发送
- `send_test_message.py` - 发送测试消息到飞书，用于测试机器人响应

### 工具脚本
- `get_chat_id.py` - 获取聊天ID，用于调试和配置

## 使用方法

1. 确保已配置 `.env` 文件，包含必要的飞书应用凭证
2. 确保机器人正在运行：
   ```bash
   python lark_bot.py
   ```
3. 运行相应的测试脚本：
   ```bash
   # 运行集成测试
   python test_scripts/run_integration_test.py
   
   # 发送测试消息
   python test_scripts/send_test_message.py
   
   # 获取聊天ID
   python test_scripts/get_chat_id.py
   ```

## 注意事项

- 这些脚本仅用于开发和测试环境
- 不要在生产环境中使用
- 确保有正确的API密钥和权限
- 测试消息会发送到真实的飞书聊天中

## 正式测试

对于单元测试和属性测试，请使用 `tests/` 目录中的测试文件：
```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_specific_feature.py
```
