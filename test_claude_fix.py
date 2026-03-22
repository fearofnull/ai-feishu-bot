"""测试 Claude CLI 执行器修复"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.xagent.executors.claude_cli_executor import ClaudeCodeCLIExecutor
from src.xagent.models import ExecutionResult

def test_claude_cli_executor():
    """测试 Claude CLI 执行器"""
    print("=" * 60)
    print("测试：Claude CLI 执行器修复")
    print("=" * 60)
    
    # 创建执行器实例
    executor = ClaudeCodeCLIExecutor(
        target_dir="/Users/proxtse/develop/TraeProjects/lark-bot",
        timeout=60
    )
    
    # 测试基本功能
    user_prompt = "你好"
    additional_params = {
        "user_id": "test_user_123",
        "username": "test_username",
        "chat_id": "test_chat_456",
        "session_id": "test_session_789",
        "original_message": "你好"
    }
    
    print(f"测试输入: {user_prompt}")
    print(f"额外参数: {additional_params}")
    
    # 执行命令
    result = executor.execute(user_prompt, additional_params=additional_params)
    
    print(f"\n执行结果:")
    print(f"成功: {result.success}")
    print(f"返回码: {'0 (成功)' if result.success else '1 (失败)'}")
    print(f"执行时间: {result.execution_time:.2f} 秒")
    
    if result.success:
        print(f"\n响应内容:")
        print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
        return True
    else:
        print(f"\n错误信息:")
        print(result.error_message)
        print(f"\n标准错误:")
        print(result.stderr)
        return False

if __name__ == "__main__":
    success = test_claude_cli_executor()
    if success:
        print("\n✓ 测试通过")
    else:
        print("\n✗ 测试失败")
        sys.exit(1)
