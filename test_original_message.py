"""测试原始消息内容传递"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.xagent.agents.react_agent import XAgent
from src.xagent.core.provider_config_manager import ProviderConfigManager
from agentscope.message import Msg

def test_original_message():
    """测试原始消息内容传递"""
    print("=" * 60)
    print("测试：原始消息内容传递")
    print("=" * 60)
    
    # 初始化 ProviderConfigManager
    provider_config_manager = ProviderConfigManager()
    print("✓ ProviderConfigManager 初始化成功")
    
    # 获取默认配置
    default_config = provider_config_manager.get_default()
    if not default_config:
        print("✗ 未找到默认提供商配置")
        return False
    
    print(f"✓ 默认提供商: {default_config.name}, 类型: {default_config.type}")
    
    # 设置环境变量
    if default_config.type in ["openai", "openai_compatible"]:
        os.environ["OPENAI_API_KEY"] = default_config.api_key
        os.environ["OPENAI_MODEL"] = default_config.default_model
        os.environ["OPENAI_BASE_URL"] = default_config.base_url
        print("✓ 已设置 OpenAI 环境变量")
    
    # 规范化提供商类型
    normalized_provider_type = default_config.type
    if normalized_provider_type == "openai_compatible":
        normalized_provider_type = "openai"
    
    # 创建 XAgent 实例
    agent = XAgent(provider_type=normalized_provider_type)
    print("✓ XAgent 初始化成功")
    
    # 测试：传递原始消息内容
    print("\n测试：传递原始消息内容")
    original_message = "你好"
    msg = Msg(name="User", content="请使用中文回答以下问题：\n\n你好", role="user")
    
    # 模拟完整的用户信息
    test_user_id = "test_user_123"
    test_username = "test_username"
    test_chat_id = "test_chat_456"
    test_session_id = "test_session_789"
    
    import asyncio
    try:
        response = asyncio.run(agent.reply(
            msg,
            user_id=test_user_id,
            username=test_username,
            chat_id=test_chat_id,
            session_id=test_session_id,
            original_message=original_message
        ))
        response_content = ""
        
        # 提取响应内容
        if response.content:
            if isinstance(response.content, str):
                response_content = response.content
            elif isinstance(response.content, list):
                for item in response.content:
                    if isinstance(item, dict) and item.get("type") == "text" and "text" in item:
                        response_content = item["text"]
                        break
        
        print(f"原始消息: {original_message}")
        print(f"实际消息（带语言提示词）: {msg.content}")
        print(f"Agent 响应: {response_content}")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 验证审计日志
    print("\n验证审计日志")
    import json
    from pathlib import Path
    from datetime import datetime, timezone
    
    log_dir = Path("./data/audit_logs")
    if log_dir.exists():
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = log_dir / f"audit_{date_str}.log"
        
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    user_input_preview = last_entry.get("metadata", {}).get("user_input_preview", "")
                    
                    print(f"审计日志记录的输入: {user_input_preview}")
                    
                    # 检查是否记录了原始消息内容
                    if original_message in user_input_preview:
                        print("✓ 审计日志正确记录了原始消息内容")
                        return True
                    else:
                        print(f"✗ 审计日志未正确记录原始消息内容")
                        print(f"  期望包含: {original_message}")
                        print(f"  实际记录: {user_input_preview}")
                        return False
                else:
                    print("✗ 审计日志为空")
                    return False
        else:
            print(f"✗ 审计日志文件不存在: {log_file}")
            return False
    else:
        print(f"✗ 审计日志目录不存在: {log_dir}")
        return False

if __name__ == "__main__":
    success = test_original_message()
    if success:
        print("\n✓ 测试通过")
    else:
        print("\n✗ 测试失败")
        sys.exit(1)
