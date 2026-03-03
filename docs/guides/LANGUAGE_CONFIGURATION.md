# 语言配置说明

## 概述

飞书AI机器人支持配置AI回复的语言。通过设置 `RESPONSE_LANGUAGE` 环境变量，你可以让AI使用指定的语言回复用户消息。

## 配置方法

### 1. 在 `.env` 文件中配置

编辑 `.env` 文件，添加或修改 `RESPONSE_LANGUAGE` 配置：

```bash
# 设置为中文（简体）
RESPONSE_LANGUAGE=zh-CN

# 设置为英语
RESPONSE_LANGUAGE=en-US

# 设置为日语
RESPONSE_LANGUAGE=ja-JP

# 不设置（由AI自动判断）
RESPONSE_LANGUAGE=
```

### 2. 支持的语言代码

| 语言代码 | 语言名称 |
|---------|---------|
| `zh-CN` | 中文（简体） |
| `zh-TW` | 中文（繁體） |
| `en-US` | English |
| `en-GB` | English (UK) |
| `ja-JP` | 日本語 |
| `ko-KR` | 한국어 |
| `fr-FR` | Français |
| `de-DE` | Deutsch |
| `es-ES` | Español |
| `ru-RU` | Русский |
| `pt-BR` | Português (Brasil) |
| `it-IT` | Italiano |
| `ar-SA` | العربية |
| `hi-IN` | हिन्दी |

## 工作原理

当你设置了 `RESPONSE_LANGUAGE` 后，系统会在每次调用AI时自动在用户消息前添加语言指令。

### 示例

**配置**：
```bash
RESPONSE_LANGUAGE=zh-CN
```

**用户消息**：
```
What is Python?
```

**实际发送给AI的消息**：
```
Please respond in 中文（简体）.

What is Python?
```

**AI回复**：
```
Python是一种高级编程语言，由Guido van Rossum于1991年创建...
```

## 使用场景

### 场景1：多语言团队

如果你的团队成员来自不同国家，但希望AI统一使用某种语言回复：

```bash
# 团队统一使用英语
RESPONSE_LANGUAGE=en-US
```

### 场景2：学习外语

如果你想通过与AI对话来学习某种语言：

```bash
# 学习日语
RESPONSE_LANGUAGE=ja-JP
```

### 场景3：自动判断

如果你希望AI根据用户输入的语言自动选择回复语言：

```bash
# 不设置，让AI自动判断
RESPONSE_LANGUAGE=
```

这种情况下：
- 用户用中文提问 → AI用中文回复
- 用户用英文提问 → AI用英文回复

## 注意事项

1. **语言指令不是强制的**：AI会尽量遵守语言指令，但在某些情况下可能会使用其他语言（例如代码注释、专业术语等）。

2. **CLI工具的语言支持**：
   - Claude Code CLI 和 Gemini CLI 都支持语言指令
   - 但某些CLI输出（如命令执行结果）可能不受语言配置影响

3. **性能影响**：添加语言指令会略微增加token消耗，但影响很小。

4. **重启生效**：修改 `.env` 文件后需要重启机器人才能生效。

## 验证配置

启动机器人后，你会在日志中看到语言配置信息：

```
配置状态
============================================================
...
RESPONSE_LANGUAGE: zh-CN
...
============================================================
```

如果显示 `⚠️ 未设置（由AI自动判断）`，说明没有配置语言，AI会自动判断。

## 故障排除

### 问题1：AI没有使用指定语言回复

**可能原因**：
- 配置文件未正确加载
- 机器人未重启
- AI模型不支持该语言

**解决方法**：
1. 检查 `.env` 文件中的配置是否正确
2. 重启机器人
3. 查看日志确认配置已加载
4. 尝试使用更常见的语言（如 `zh-CN` 或 `en-US`）

### 问题2：语言代码不生效

**可能原因**：
- 语言代码拼写错误
- 使用了不支持的语言代码

**解决方法**：
1. 参考上面的"支持的语言代码"表格
2. 确保使用正确的格式（如 `zh-CN` 而不是 `zh_CN`）
3. 如果需要其他语言，可以直接使用语言名称（如 `RESPONSE_LANGUAGE=Vietnamese`）

## 高级用法

### 自定义语言指令

如果你需要更精细的控制，可以修改 `feishu_bot/config.py` 中的 `get_language_instruction()` 方法：

```python
def get_language_instruction(self) -> str:
    """获取语言指令文本"""
    if not self.response_language:
        return ""
    
    # 自定义语言指令格式
    return f"请用{self.response_language}回复，并使用专业术语。"
```

### 动态语言切换

目前语言配置是全局的，如果需要为不同用户设置不同语言，可以考虑：

1. 在数据库中存储用户语言偏好
2. 在消息处理时动态添加语言指令
3. 修改 `feishu_bot.py` 中的消息处理逻辑

这需要自定义开发，不在默认功能范围内。

## 相关文档

- [配置文档](CONFIGURATION.md)
- [快速开始](../README.md#快速开始)
- [环境变量模板](../.env.example)
